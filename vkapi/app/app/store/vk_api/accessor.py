import json
import random
import typing
from typing import Optional

from aiohttp import ClientSession, TCPConnector

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.poller import Poller
from app.store.vk_api.keyboard import keyboard_close


if typing.TYPE_CHECKING:
    from app.web.app import Application

PATH_API = "https://api.vk.com/method/"
COUNT_STOP = 0

class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        try:
            await self._get_long_poll_service()
        except Exception as e:
            self.logger.error("Exception", exc_info=e)
        self.poller = Poller(logger=self.logger, store=app.store)
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.poller:
            await self.poller.stop()
        if self.session:
            await self.session.close()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        async with self.session.get(
            self._build_query(
                host=PATH_API,
                method="groups.getLongPollServer",
                params={
                    "group_id": self.app.config.bot.group_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as response:
            data = (await response.json())['response']
            self.key = data['key']
            self.server = data['server']
            self.ts = data['ts']
            self.logger.info(self.server)

    async def poll(self):
        self.app.logger.info('new poll request')
        async with self.session.get(
            self._build_query(
                host=self.server,
                method='',
                params={
                    'act': 'a_check',
                    'key': self.key,
                    'ts': self.ts,
                    'wait': 25,
                },
            )
        ) as response:
            data = await response.json()
            self.app.logger.info(data)

            global COUNT_STOP
            if 'failed' in data:
                COUNT_STOP += 1
            elif COUNT_STOP == 5:
                raise "LONG POLL RASE"

            # self.ts = data['ts']
            if not data.get('ts'):
                await self._get_long_poll_service()
            else:
                self.ts = data['ts']

            return data['updates']

    async def send_message_vk(
            self,
            message: dict,
            destination: str = 'peer_id',
            method: str = "messages.send",
            keyboard: dict = keyboard_close) -> None:

        query = self._build_query(
                host=PATH_API,
                method=method,
                params={
                    'random_id': random.randint(1, 2 ** 32),
                    destination: message[destination],
                    'message': message.get('text'),
                    'access_token': self.app.config.bot.token,
                    'event_id': message.get('event_id'),
                    'peer_id': message.get('peer_id'),
                    'event_data': message.get('event_data')
                },
            )

        keyboard = keyboard if keyboard else keyboard_close
        keyboard = json.dumps(keyboard)
        query = query + "&keyboard=" + keyboard

        async with self.session.get(
                query
        ) as response:
            data = await response.json()
            self.logger.info(data)

            message: dict = {}
            try:
                message['profiles'] = data['response']['profiles']
                message['command'] = 'start_game'
                await self.app.store.queue.publish(queue='bot', message=message)
            except KeyError:
                pass
            except TypeError:
                pass
