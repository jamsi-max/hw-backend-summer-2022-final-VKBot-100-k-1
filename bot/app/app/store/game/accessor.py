from logging import getLogger
from random import choice
from typing import List, Optional

from sqlalchemy import select, desc
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.orm import joinedload

from app.base.base_accessor import BaseAccessor
from app.game.models import (
    GamesAnswers,
    GameModel,
    PlayerModel,
    PlayersGames,
)
from app.quiz.models import AnswerModel, QuestionModel


class GameAccessor(BaseAccessor):
    logger = getLogger("handler")
    game_id: int = None
    game_run: bool = False
    current_score: int = 0
    question_id: int = None
    responder: int = None
    winner: int = None
    players: list = []
    answers: dict = {}

    async def connect(self, app: "Application") -> None:
        await super().connect(app)
        self.logger.info('[bor] GameAccesor connect bd...')
        try:
            async with app.database.session() as s:
                async with self.app.database.session() as s:
                    result = await s.execute(
                        select(GameModel)
                        .where(GameModel.is_run == True)
                        .options(joinedload(GameModel.players))
                        .options(joinedload(GameModel.answers_right))
                    )
                    game_obj: Optional[GameModel] = result.scalar()

                    if game_obj:
                        self.game_id = game_obj.id
                        self.game_run = game_obj.is_run
                        self.current_score = game_obj.current_score
                        self.responder = game_obj.responder
                        self.winner = game_obj.winner
                        self.question_id = game_obj.question_id
                        self.players = [
                            player.player_id for player in game_obj.players
                        ]
                        if game_obj.answers_right:
                            for answer in game_obj.answers_right:
                                answer_obj: AnswerModel = (
                                    await self.get_answers_by_id(answer.answers_id)
                                )
                                self.answers[answer_obj.rating] = (
                                    answer_obj.title,
                                    answer_obj.points
                                )
        except ProgrammingError:
            pass

    async def add_bd(self, obj: any) -> None:
        async with self.app.database.session() as s:
            s.add(obj)
            await s.commit()

    async def start(self, data: dict):
        if self.game_run:
            data['text'] = 'Игра уже идёт! Вы можете присоединиться!'
            data['keyboard'] = 'keyboard_game_join'
            await self.app.store.queue.publish(queue='vk_api', message=data)
            return

        if 'profiles' in data:
            self.players = [
                profile['id'] for profile in data['profiles'] if profile['online'] == 1
            ]

        if not self.players:
            data['method'] = 'messages.getConversationMembers'
            await self.app.store.queue.publish(queue='vk_api', message=data)
            return

        question: QuestionModel = choice(await self.get_questions())

        new_game = GameModel(
            question_id=question.id
        )
        await self.add_bd(new_game)
        self.question_id = question.id

        for player_id in self.players:
            player_game = PlayersGames(
                game_id=new_game.id,
                player_id=player_id
            )
            await self.add_bd(player_game)

        self.game_run = new_game.is_run
        self.game_id = new_game.id
        data['keyboard'] = 'keyboard_responder'
        data['text'] = f'!!!Начинаем игру!!! <br>' \
                       f'Внимание вопрос: <br> {question.title} <br>' \
                       f'1. XXXXXXX <br>' \
                       f'2. XXXXXXX <br>' \
                       f'3. XXXXXXX <br>' \
                       f'4. XXXXXXX <br>' \
                       f'5. XXXXXXX <br>' \
                       f'6. XXXXXXX'
        data['peer_id'] = self.app.store.manager.CHAT_GAME_ID
        await self.app.store.queue.publish(queue='vk_api', message=data)

        self.logger.info('[bot] game run')

    async def join(self, data: dict) -> None:
        player: PlayerModel = await self.get_player(int(data["user_id"]))

        if player.vk_user_id not in self.players:
            new_player_game = PlayersGames(
                player_id=player.vk_user_id,
                game_id=self.game_id
            )
            await self.add_bd(new_player_game)
            self.players.append(player.vk_user_id)
            data['text'] = f'{player.name} присоединился к игре!'

        if self.game_run and not self.responder:
            data['keyboard'] = 'keyboard_responder'
        elif self.game_run and self.responder:
            data['keyboard'] = 'keyboard_game_stop'

        await self.app.store.queue.publish(queue='vk_api', message=data)
        self.logger.info('[bot] join game')

    async def stop(self, data: dict) -> None:
        if await self.check_not_game_run(data):
            return

        game = await self.get_game(self.game_id)
        game.is_run = False

        await self.add_bd(game)

        data['keyboard'] = 'keyboard_game_start'
        data['text'] = 'Игра окончена!'
        await self.app.store.queue.publish(queue='vk_api', message=data)

        self.game_run = game.is_run
        self.game_id = None
        self.current_score = 0
        self.responder = None
        self.winner = None
        self.players = []
        self.question_id = None
        self.answers = {}

        await self.info(
            data=data,
            keyboard='keyboard_game_start'
        )

    async def info(self, data: dict, keyboard: str = None) -> None:
        game: GameModel = await self.get_game()
        question: QuestionModel = await self.get_questions(game.question_id)
        player: PlayerModel = await self.get_player(game.winner)
        data['keyboard'] = keyboard

        data['text'] = f'Информация об игре! <br>' \
                       f'Статус: {"идёт" if game.is_run else "окончена"} <br>' \
                       f'Начало игры: {game.created:%Y-%m-%d %H:%M} <br>' \
                       f'Заработано очков {game.current_score} <br>' \
                       f'Победитель: {"не определён" if player is None else player.name} <br>' \
                       f'Всего игроков: {len(game.players)} <br>' \
                       f'Вопрос: {question.title}'

        await self.app.store.queue.publish(queue='vk_api', message=data)

    async def check_answer(self, data: dict):
        if await self.check_not_game_run(data):
            return
        answer: AnswerModel = await self.find_answers(data["text"])

        if answer:
            self.answers[answer.rating] = (answer.title, answer.points)
            self.current_score += answer.points
            game: GameModel = await self.get_game(self.game_id)
            game.current_score = self.current_score
            await self.add_bd(game)

            game_answer: GamesAnswers = GamesAnswers(
                answers_id=answer.id,
                game_id=game.id
            )

            try:
                await self.add_bd(game_answer)
            except IntegrityError:
                self.responder = None
                game: GameModel = await self.get_game(self.game_id)
                game.responder = self.responder
                await self.add_bd(game)
                data['keyboard'] = 'keyboard_responder'
                data['text'] = 'Этот ответ уже назван! <br>' \
                               'Переход хода! <br>' \
                               'Кто хочет ответить жмите кнопку!'
                await self.app.store.queue.publish(queue='vk_api', message=data)
                await self.show_current_answers(data)
                return

            player_game: PlayersGames = await self.get_player_game(self.responder)
            player_game.player_game_score += answer.points
            await self.add_bd(player_game)

            player: PlayerModel = await self.get_player(self.responder)
            player.score += answer.points
            await self.add_bd(player)

            if len(self.answers) == 6:
                await self.set_winner(data=data, winner=self.responder)
                return

            await self.show_current_answers(data)
            data['text'] = f'Верно! <br>' \
                           f'Твой счёт: {player_game.player_game_score}! <br>' \
                           f'{player.name} продолжает отвечать!'
            await self.app.store.queue.publish(queue='vk_api', message=data)
        else:
            self.responder = None
            game = await self.get_game(self.game_id)
            game.responder = self.responder
            await self.add_bd(game)
            data['keyboard'] = 'keyboard_responder'
            data['text'] = 'Ответ не верный! <br>' \
                           'Кто хочет ответить жмите кнопку!'
            await self.app.store.queue.publish(queue='vk_api', message=data)

    async def check_not_game_run(self, data: dict):
        if not self.game_run:
            data['keyboard'] = 'keyboard_game_start'
            data['text'] = 'Игра не найдена!'
            await self.app.store.queue.publish(queue='vk_api', message=data)
            return True
        return False

    async def get_questions(self, questions_id: int = None) -> List[QuestionModel]:
        query = select(QuestionModel)
        if questions_id:
            query = (
                query.where(QuestionModel.id == questions_id)
            )
        async with self.app.database.session() as s:
            result = await s.execute(query)
        result = result.scalars().all()

        if len(result) != 1:
            return result
        return result[0]

    async def get_answers_by_id(self, answers_id: int) -> Optional[AnswerModel]:
        async with self.app.database.session() as s:
            result = await s.execute(
                select(AnswerModel)
                .where(AnswerModel.id == answers_id)
            )
            if result:
                return result.scalars().first()
            return None

    async def get_game(self, game_id: int = None) -> Optional[GameModel]:
        query = select(GameModel)
        if game_id:
            query = query.where(GameModel.id == game_id)

        async with self.app.database.session() as s:
            result = await s.execute(
                query
                .options(joinedload(GameModel.players))
                .order_by(desc(GameModel.created))
            )
            if result:
                return result.scalar()
            return None

    async def get_player(self, player_id) -> Optional[PlayerModel]:
        async with self.app.database.session() as s:
            result = (
                (
                    await s.execute(
                        select(PlayerModel).where(PlayerModel.vk_user_id == player_id)
                    )
                )
                .scalars()
                .first()
            )
            if result:
                return result
            return None

    async def get_player_game(self, player_id: int) -> PlayersGames:
        async with self.app.database.session() as s:
            result = (
                (
                    await s.execute(
                        select(PlayersGames)
                        .where(PlayersGames.game_id == self.game_id)
                        .where(PlayersGames.player_id == player_id)
                    )
                )
                .scalars()
                .first()
            )
            if result:
                return result
            return None

    async def set_winner(self, data: dict, winner: int) -> None:
        game: GameModel = await self.get_game(self.game_id)
        game.winner = winner
        await self.add_bd(game)

        player: PlayerModel = await self.get_player(winner)
        player_game: PlayersGames = await self.get_player_game(winner)

        data['text'] = f'Победитель {player.name}! <br>' \
                       f'{player.name} заработал {player_game.player_game_score} <br>' \
                       f'Всего очков у {player.name} - {player.score}'
        await self.app.store.queue.publish(queue='vk_api', message=data)
        await self.stop(data)

    async def set_responder(self, data: dict) -> None:
        if await self.check_not_game_run(data):
            return

        if self.game_run and not self.responder:
            self.responder = data['user_id']

            game = await self.get_game(self.game_id)
            game.responder = self.responder
            await self.add_bd(game)

            player: PlayerModel = await self.get_player(int(data['user_id']))
            data['keyboard'] = 'keyboard_game_stop'
            data['text'] = f'Отвечает {player.name} <br>' \
                           f'Остальные игроки ожидают!'
            await self.app.store.queue.publish(queue='vk_api', message=data)
        else:
            data['keyboard'] = 'keyboard_game_stop'
            data['text'] = ''
            await self.app.store.queue.publish(queue='vk_api', message=data)

    async def find_answers(self, answer: int) -> Optional[AnswerModel]:
        async with self.app.database.session() as s:
            result = await s.execute(
                select(AnswerModel)
                .where(AnswerModel.question_id == self.question_id)
                .filter(AnswerModel.title.like(answer.lower()))
            )
            answer: AnswerModel = result.scalars().first()
            if answer:
                return answer
            return None

    async def show_current_answers(self, data: dict) -> None:
        answer_total = ''
        for i in range(1, 7):
            if self.answers.get(i):
                answer_total += f'{i}) - {self.answers.get(i)[0]} {self.answers.get(i)[1]} <br>'
            else:
                answer_total += f'{i}) - XXXXXXXX <br>'
        data['text'] = answer_total
        await self.app.store.queue.publish(queue='vk_api', message=data)
