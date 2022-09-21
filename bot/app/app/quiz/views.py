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

from app.quiz.models import Answer, Theme
from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    ThemeIdSchema,
    ThemeListSchema,
    ThemeSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @request_schema(ThemeSchema)
    @docs(
        tags=['VKBot'],
        summary='Adding a new theme',
        description='Add new theme in database'
    )
    @response_schema(ThemeSchema)
    async def post(self) -> Response:
        try:
            theme = await self.store.quizzes.create_theme(
                title=self.data["title"]
            )
        except IntegrityError as e:
            raise HTTPConflict

        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    @docs(
        tags=['VKBot'],
        summary='List all themes',
        description='List all themes from database'
    )
    @response_schema(ThemeListSchema)
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response(data=ThemeListSchema().dump({"themes": themes}))


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
        theme_id = self.data.get('theme_id')
        answers = [
            Answer(
                title=answer["title"],
                is_correct=answer["is_correct"]
            ) for answer in self.data.get('answers')
        ]
        if len(set(a.is_correct for a in answers)) == 1:
            raise HTTPBadRequest
        try:
            question = await self.store.quizzes.create_question(
                title=title,
                theme_id=theme_id,
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
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        questions = await self.store.quizzes.list_questions(
            theme_id=self.data.get("theme_id")
        )
        return json_response(
            data=ListQuestionSchema().dump(
                {
                    "questions": questions
                }
            )
        )
