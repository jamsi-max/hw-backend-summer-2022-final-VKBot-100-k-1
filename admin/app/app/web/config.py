import os
import typing
import yaml
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class SessionConfig:
    key: str


@dataclass
class AdminConfig:
    email: str
    password: str


@dataclass
class DatabaseConfig:
    host: str = ""
    port: int = 0
    user: str = ""
    password: str = ""
    database: str = ""


@dataclass
class Config:
    admin: AdminConfig
    session: SessionConfig = None
    database: DatabaseConfig = None


def setup_config(app: "Application", config_path: str):
    # with open(config_path, "r") as f:
    #     raw_config = yaml.safe_load(f)

    app.config = Config(
        session=SessionConfig(
            key=os.environ.get('SESSION_KEY'),
        ),
        admin=AdminConfig(
            email=os.environ.get('ADMIN_EMAIL'),
            password=os.environ.get('ADMIN_PASSWORD'),
        ),
        database=DatabaseConfig(
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD'),
            database=os.environ.get('POSTGRES_DB'),
        ),
    )
