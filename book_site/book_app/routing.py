from django.conf import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from book_app.consumers import DiscussionConsumer
application = ProtocolTypeRouter({
    'websocket':AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    path('book_preview/<str:id>', DiscussionConsumer),
                ]
            )
        )
    )
})