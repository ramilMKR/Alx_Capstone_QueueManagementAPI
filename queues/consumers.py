import json
from channels.generic.websocket import AsyncWebsocketConsumer

class QueueConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.queue_id = self.scope['url_route']['kwargs']['queue_id']
        self.group_name = f'queue_{self.queue_id}'

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from server
    async def queue_update(self, event):
        await self.send(text_data=json.dumps(event['data']))