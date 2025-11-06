"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from game.consumers import MatchStreamConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

django_app = get_asgi_application()

websocket_urlpatterns = [
    re_path(r"^matches/(?P<match_id>[0-9a-f\-]+)/stream$", MatchStreamConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": django_app,
    "websocket": URLRouter(websocket_urlpatterns),
})
