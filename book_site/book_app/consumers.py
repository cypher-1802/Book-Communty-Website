import asyncio
import json
from regex import F
import requests
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

from .models import Discussion

class DiscussionConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print("connected", event)
        await self.send({
            "type" : "websocket.accept"
        })

        id = self.scope['url_route']['kwargs']['id']
        # me = self.scope['user']

        discuss_obj = await self.Discuss(id)

        # print(discuss_obj)


    async def websocket_receive(self, event):
        print("receive", event)
        front_text = event.get('text', None)
        if front_text is not None:
            loaded_dict_data = json.loads(front_text)
            msg = loaded_dict_data.get('message')
            print(msg)
            myResponse = {
                'message' : msg,
            }
            await self.send({
                "type" : "websocket.send",
                "text" : json.dumps(myResponse)
            })

    async def websocket_disconnect(self, event):
        print("disconnected", event)

    @database_sync_to_async
    def Discuss(self, id):
        name = requests.get('https://www.googleapis.com/books/v1/volumes/'+id+'?key=AIzaSyC887_T5c9ZEkD9tMzzDB2e_1Dv_5sJ7L0').json()
        return Discussion.objects.filter(book_id = name['id']).order_by("-created_on")[:50]
