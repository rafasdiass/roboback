# asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import automacao.routing  # Importe o routing do seu app 'automacao'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robotrader.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Defina a rota do WebSocket
    "websocket": AuthMiddlewareStack(
        URLRouter(
            automacao.routing.websocket_urlpatterns
        )
    ),
})
