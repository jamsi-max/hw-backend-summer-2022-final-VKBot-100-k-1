from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.base.base_accessor import BaseAccessor
from app.quiz.models import (
    Answer,
    AnswerModel,
    Question,
    QuestionModel,
)


class QuizAccessor(BaseAccessor):

    async def create_question(
        self, title: str, answers: list[Answer]
    ) -> Question:
        new_question = QuestionModel(
            title=title,
            answers=[
                AnswerModel(
                    title=answer.title,
                    points=answer.points,
                ) for answer in answers
            ],
        )
        async with self.app.database.session.begin() as s:
            s.add(new_question)

        return new_question.get_object()

    async def get_question_by_title(self, title: str) -> Optional[Question]:
        async with self.app.database.session() as s:
            result = await s.execute(
                select(QuestionModel)
                .where(QuestionModel.title == title)
                .options(joinedload(QuestionModel.answers))
            )

            question_obj: Optional[QuestionModel] = result.scalar()
            if question_obj is None:
                return

            return question_obj.get_object()

    async def list_questions(self, theme_id: int = None) -> list[Question]:

        query = select(QuestionModel)
        if theme_id:
            query = query.where(QuestionModel.theme_id == theme_id)
        async with self.app.database.session() as s:
            result = await s.execute(
                query.options(joinedload(QuestionModel.answers))
            )
        return [o.get_object() for o in result.scalars().unique()]
