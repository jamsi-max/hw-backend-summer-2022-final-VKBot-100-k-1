import typing


if typing.TYPE_CHECKING:
    from app.web.app import Application



class Store:
    def __init__(self, app: "Application"):
        self.app = app
        from app.store.vk_api.accessor import VkApiAccessor
        from app.store.queue.accessor import QueueConnectAccessor

        self.vk_api = VkApiAccessor(app)
        self.queue = QueueConnectAccessor(app)


def setup_store(app: "Application"):
    app.store = Store(app)
