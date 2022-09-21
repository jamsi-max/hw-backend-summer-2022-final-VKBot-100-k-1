from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.store.database.sqlalchemy_base import db
from app.quiz.models import AnswerModel, QuestionModel


class PlayersGames(db):
    __tablename__ = "players_games"

    player_id = Column(ForeignKey("players.vk_user_id"), primary_key=True)
    game_id = Column(ForeignKey("games.id"), primary_key=True)
    player_game_score = Column(Integer, default=0)

    players = relationship("PlayerModel")


class GamesAnswers(db):
    __tablename__ = "games_answers"

    answers_id = Column(ForeignKey("answers.id"), primary_key=True)
    game_id = Column(ForeignKey("games.id"), primary_key=True)

    answers = relationship("AnswerModel")

@dataclass
class Player:
    id: int
    name: str
    vk_user_id: int
    score: int
    created: str


class PlayerModel(db):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    vk_user_id = Column(Integer, nullable=False, unique=True)
    score = Column(Integer, default=0)
    created = Column(DateTime(timezone=True), server_default=func.now())

    def get_object(self) -> Player:
        return Player(
            id=self.id,
            name=self.name,
            vk_user_id=self.vk_user_id,
            score=self.score,
            created=self.created,
        )


@dataclass
class Game:
    id: int
    is_run: bool
    created: str
    current_score: int
    responder: Optional[int] = None
    players: list["Player"] = field(default_factory=list)
    winner: Optional[int] = None


class GameModel(db):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    is_run = Column(Boolean, default=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    current_score = Column(Integer, default=0)
    question_id = Column(
        Integer,
        ForeignKey("questions.id"),
        nullable=True)
    responder = Column(
        Integer,
        ForeignKey("players.vk_user_id"),
        nullable=True
    )
    winner = Column(
        Integer,
        ForeignKey("players.vk_user_id"),
        nullable=True
    )
    players = relationship("PlayersGames")
    answers_right = relationship("GamesAnswers")

    def get_object(self) -> Game:
        return Game(
            id=self.id,
            is_run=self.is_run,
            created=self.created,
            current_score=self.current_score,
            responder=self.responder,
            winner=self.winner,
            players=[player.get_object() for player in self.players]
        )
