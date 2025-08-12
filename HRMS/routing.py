
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from HRMS.routing import websocket_urlpatterns
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        'websocket': URLRouter(websocket_urlpatterns),
    }
)
