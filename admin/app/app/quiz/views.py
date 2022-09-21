from typing import List, Optional

from aiohttp.web_response import Response
from aiohttp_apispec import (
    docs,
    querystring_schema,
    request_schema,
    response_schema
)
from aiohttp.web_exceptions import (
    HTTPBadRequest,
    HTTPNotFound,
    HTTPConflict,
)
from sqlalchemy.exc import IntegrityError

from app.quiz.models import Answer
from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class QuestionAddView(AuthRequiredMixin, View):
    @docs(
        tags=['VKBot'],
        summary='Adding a new question',
        description='Adding a new question in database'
    )
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        title = self.data.get('title')
        answers = [
            Answer(
                rating=answer["rating"],
                title=answer["title"],
                points=answer["points"]
            ) for answer in self.data.get('answers')
        ]

        if len(set(a.title for a in answers)) < 6:
            raise HTTPBadRequest

        try:
            question = await self.store.quizzes.create_question(
                title=title,
                answers=answers
            )
        except IntegrityError as e:
            raise HTTPNotFound

        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(AuthRequiredMixin, View):
    @docs(
        tags=['VKBot'],
        summary='List all Questions',
        description='List all Questions from database'
    )
    @response_schema(ListQuestionSchema)
    async def get(self):
        questions = await self.store.quizzes.list_questions()
        return json_response(
            data=ListQuestionSchema().dump(
                {
                    "questions": questions
                }
            )
        )
