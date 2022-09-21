from dataclasses import dataclass, field

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import db


@dataclass
class Answer:
    rating: int
    title: str
    points: int


class AnswerModel(db):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    rating = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    points = Column(Integer, nullable=False)
    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE")
    )

    def get_object(self) -> Answer:
        return Answer(rating=self.rating, title=self.title, points=self.points)


@dataclass
class Question:
    id: int
    title: str
    answers: list["Answer"] = field(default_factory=list)


class QuestionModel(db):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True)
    answers = relationship("AnswerModel")

    def get_object(self) -> Question:
        return Question(
            id=self.id,
            title=self.title,
            answers=[answer.get_object() for answer in self.answers]
        )
