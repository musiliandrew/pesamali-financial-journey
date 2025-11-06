import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import GameRooms

class MatchStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs'].get('match_id')
        try:
            GameRooms.objects.get(id=self.match_id)
        except GameRooms.DoesNotExist:
            await self.close()
            return
        self.group_name = f"match_{self.match_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        return

    # Handler for events sent via channel layer
    async def game_event(self, event):
        # event['payload'] must be JSON-serializable
        await self.send(text_data=json.dumps(event['payload']))
