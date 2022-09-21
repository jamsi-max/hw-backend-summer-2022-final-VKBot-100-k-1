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

if typing.TYPE_CHECKING:
    from app.web.app import Application


class QueueConnectAccessor(BaseAccessor):
    queue = 'bot'
    amqp_host = os.environ.get('AMQP_HOST')

    async def connect(self, app: "Application") -> None:
        await super().connect(app)

        self.logger.info('[bor] start connection to the queue...')
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
            self.logger.info('[bot] service waiting for messages...')
            await asyncio.Future()

    async def _handler(self, message: AbstractIncomingMessage) -> None:
        self.logger.info('[RabbitMQ -> bot] Message received!')

        data = json.loads(message.body)
        await self.app.store.manager.handle(data)

        # print('*'*80)
        # print(data)
        # payload = json.loads(data['payload'])

        # if payload.get('registration') == 'registration':
        #     await self.app.store.game.user_registration(data)
        #
        # if not await self.app.store.game.user_check(int(data['user_id'])):
        #     data['user_not_registered'] = True
        #     data['text'] = 'Вы не зарегистрированы!'
        #     await self.publish(queue='vk_api', message=data)

        # try:
        #     data_message = data_raw['object']['message']
        # except KeyError as e:
        #     raise f'[bot] key [object][message] not found'
        #
        # if 'payload' in data_message:
        #     payload = json.loads(data_message['payload'])
        #
        # if payload.get('registration') == 'add_user':
        #     await self.registry_user(data_message)
        # else:
        #     user = await self.get_user(data_message)
        # print(f"[bot] Message body is: {data}")

    async def publish(self, queue: str, message: dict) -> None:
        raw_message = json.dumps(message)
        connection = await connect(self.amqp_host)

        async with connection:
            channel: AbstractChannel = await connection.channel()
            queue: AbstractQueue = await channel.declare_queue(
                queue,
                durable=True
            )
            await channel.default_exchange.publish(
                Message(raw_message.encode()),
                routing_key=queue.name,
            )
            self.logger.info(
                f'[bot -> RabbitMQ] Message sent to queue: {queue}'
            )

    async def get_user(self, data: dict):
        try:
            user_id = int(data['from_id'])
        except KeyError as e:
            self.logger.error(
                '[from_id] key is missing in the response!',
                exc_info=e
            )
            raise 'KeyError [from_id] not exists'

        message = {
            'user_id': user_id,
            'message': 'Вы не зарегистрированы!',
            'registered': False
        }
        await self.publish(queue='vk_api', message=message)
        return False

    async def registry_user(self, data: dict):
        print('*'*80)
        print('регистрируем пользователя')
