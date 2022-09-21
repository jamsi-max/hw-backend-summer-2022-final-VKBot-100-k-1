import asyncio
import json
import os
import typing

from aio_pika import Message, connect
from aio_pika.abc import (
    AbstractChannel,
    AbstractQueue,
    AbstractIncomingMessage
)

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message as MessageVKApi
from app.store.vk_api.keyboard import (
    keyboard_close,
    keyboard_game_start,
    keyboard_game_join,
    keyboard_game_stop,
    keyboard_responder
)

if typing.TYPE_CHECKING:
    from app.web.app import Application


class QueueConnectAccessor(BaseAccessor):
    queue: str = 'vk_api'
    amqp_host: str = os.environ.get('AMQP_HOST')
    keyboard: dict = {
        'keyboard_game_start': keyboard_game_start,
        'keyboard_game_join': keyboard_game_join,
        'keyboard_game_stop': keyboard_game_stop,
        'keyboard_responder': keyboard_responder,
        None: keyboard_close
    }

    async def connect(self, app: "Application") -> None:
        await super().connect(app)

        self.logger.info('[vk_api] start connection to the queue...')
        connection = None
        while connection is None:
            try:
                connection = await connect(self.amqp_host)
            except ConnectionError:
                await asyncio.sleep(2)

        async with connection:
            channel: AbstractChannel = await connection.channel()
            queue: AbstractQueue = await channel.declare_queue(
                self.queue,
                durable=True
            )
            await queue.consume(self._handler, no_ack=True)
            self.logger.info('[vk_api] service waiting for messages...')
            await asyncio.Future()

    async def _handler(self, message: AbstractIncomingMessage) -> None:
        self.logger.info('[RabbitMQ -> vk_api] Message received!')
        data: dict = json.loads(message.body)

        await self.app.store.vk_api.send_message_vk(
            message=data,
            keyboard=self.keyboard.get(data.get('keyboard'), None),
            destination=data.get('destination', 'peer_id'),
            method=data.get('method', 'messages.send')
        )

        # await self.app.store.vk_api.send_message_vk(
        #     message=data
        # )
        # if data.get('user_not_registered'):
        #     await self.app.store.vk_api.send_message(
        #         MessageVKApi(
        #             user_id=data['user_id'],
        #             text=data['text'],
        #             user_not_registered=data['user_not_registered']
        #         )
        #     )


        # await self.app.store.vk_api.send_message(
        #     MessageVKApi(
        #         user_id=data_message['user_id'],
        #         text=data_message['message'],
        #         registered=data_message.get('registered', True)
        #     ),
        # )

    async def publish(self, queue: str, message: dict) -> None:
        connection = await connect(self.amqp_host)
        async with connection:
            channel: AbstractChannel = await connection.channel()
            queue: AbstractQueue = await channel.declare_queue(
                queue,
                durable=True
            )
            raw_message = json.dumps(message).encode()
            await channel.default_exchange.publish(
                Message(raw_message),
                routing_key=queue.name,
            )
            self.logger.info(
                f'[vk_api -> RabbitMQ] Message sent to queue: {queue}'
            )
