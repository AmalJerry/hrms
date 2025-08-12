from django.urls import path
from app1.consumers import TimerConsumer

websocket_urlpatterns = [
    path('ws/timer/', TimerConsumer.as_asgi()),
]
