import os
import typing
from dataclasses import dataclass


if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class BotConfig:
    token: str
    group_id: int


@dataclass
class Config:
    bot: BotConfig = None


def setup_config(app: "Application", config_path: str):

    app.config = Config(
        bot=BotConfig(
            token=os.environ.get('BOT_TOKEN'),
            group_id=os.environ.get('BOT_GROUP_ID')
        )
    )
