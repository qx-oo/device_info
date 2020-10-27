# from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from devices import routing as devices_routing
from devices.middlewares import TokenAuthMiddlewareStack

application = ProtocolTypeRouter({
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(
            devices_routing.websocket_urlpatterns,
        )
    ),
})
