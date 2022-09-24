import typing
from logging import getLogger

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.game.models import PlayerModel

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    CHAT_GAME_ID = 2000000009

    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("handler")
        self.command = {
            'start_game': self.start_game,
            'join_game': self.join_game,
            'stop_game': self.stop_game,
            'info_game': self.info_game,
            'responder': self.set_responder
        }

    async def handle(self, data: dict) -> None:
        callback: str = data.get('command', None)

        if callback in self.command:
            await self.command[callback](data)
        elif int(data.get('user_id')) == self.app.store.game.responder:
            await self.check_answer(data)
        elif data['peer_id'] == self.CHAT_GAME_ID:
            data['text'] = 'Используйте кнопки для управления!'
            data['keyboard'] ='keyboard_game_start'
            await self.app.store.queue.publish(queue='vk_api', message=data)
        elif data['peer_id'] != self.CHAT_GAME_ID:
            await self.registration(data)

    async def registration(self, data):
        new_user = PlayerModel(
            name=data['text'],
            vk_user_id=data['user_id']
        )
        async with self.app.database.session() as s:
            try:
                s.add(new_user)
                await s.commit()
                data['text'] = 'Вы успешно зарегистрированы! <br>' \
                               'Переходите в чат с игрой! <br>' \
                               'https://vk.me/join/AJQ1d848/yI6J5hlwkAAU241'
                await self.app.store.queue.publish(queue='vk_api', message=data)
                self.logger.info(
                    f'User - {new_user.name} successfully registered'
                )
            except IntegrityError:
                data['text'] = 'Вы уже зарегистрированы! <br>' \
                               'Перейдите в чат с игрой! <br>' \
                               'https://vk.me/join/AJQ1d848/yI6J5hlwkAAU241'
                await self.app.store.queue.publish(queue='vk_api', message=data)

    async def check_user(self, data: dict) -> bool:
        async with self.app.database.session() as s:
            result = (
                (
                    await s.execute(
                        select(PlayerModel).where(PlayerModel.vk_user_id == int(data['user_id']))
                    )
                )
                .scalars()
                .first()
            )

        if not result:
            data['text'] = 'Вы не зарегистрированы! ' \
                           'Отправьте имя для регистрации!'
            data['destination'] = 'user_id'
            await self.app.store.queue.publish(queue='vk_api', message=data)
            return False
        data['username'] = result.name
        return True

    async def start_game(self, data: dict):
        if 'user_id' in data and await self.check_user(data):
            await self.app.store.game.start(data)
        elif 'profiles' in data:
            await self.app.store.game.start(data)

    async def stop_game(self, data: dict):
        if 'user_id' in data and await self.check_user(data):
            await self.app.store.game.stop(data)

    async def set_responder(self, data: dict):
        if 'user_id' in data and await self.check_user(data):
            await self.app.store.game.set_responder(data)

    async def join_game(self, data: dict):
        if 'user_id' in data and await self.check_user(data):
            await self.app.store.game.join(data)

    async def info_game(self, data: dict):
        if 'user_id' in data and await self.check_user(data):
            await self.app.store.game.info(data=data)

    async def check_answer(self, data: dict):
        if 'user_id' in data and await self.check_user(data):
            await self.app.store.game.check_answer(data)
