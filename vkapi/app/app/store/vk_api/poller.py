import json
import typing
from typing import Optional
from asyncio import Task, Future
import asyncio

from aiohttp import ClientOSError

from app.store.vk_api.dataclasses import (
    Message,
    Update,
    UpdateObject,
    UpdateMessage,
)

if typing.TYPE_CHECKING:
    from app.store import Store


class Poller:
    def __init__(self, logger, store: 'Store'):
        self.logger = logger
        self.store = store
        self.is_running = False
        self.poll_task: Optional[Task] = None

    def _done_callback(self, future: Future):
        if future.exception():
            self.store.app.logger.exception(
                'polling failed',
                exc_info=future.exception()
            )

    async def start(self) -> None:
        self.poll_task = asyncio.create_task(self.poll())
        self.poll_task.add_done_callback(self._done_callback)
        self.is_running = True

    async def stop(self) -> None:
        self.is_running = False
        if self.poll_task:
            await asyncio.wait([self.poll_task], timeout=26)

    async def poll(self) -> None:
        while self.is_running:
            try:
                raw_updates = await self.store.vk_api.poll()
            except ClientOSError:
                continue

            for raw_update in raw_updates:
                await self._handler(raw_update)

    async def _handler(self, update: dict) -> None:
        try:
            data = update['object']['message']
        except KeyError as e:
            self.logger.error('[vk_api] key [object][message] not found')
            raise '[vk_api] key [object] or [message] not found'

        if 'payload' in data:
            command = json.loads(data['payload']).get('command')
        else:
            command = None

        message = {
            'user_id': data['from_id'],
            'peer_id': data['peer_id'],
            'text': data['text'],
            'command': command
        }
        # https://vk.me/join/AJQ1d848/yI6J5hlwkAAU241
        # message['text'] = 'https://vk.me/join/AJQ1d848/yI6J5hlwkAAU241'
        # await self.store.vk_api.send_message_vk(message, method='messages.send')
        await self.store.queue.publish(queue='bot', message=message)
