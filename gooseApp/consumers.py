from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ChatConsumer(AsyncWebsocketConsumer): 
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_channel_name = f'chat_{self.user_id}'
        print(f"connected to WebSocket: {self.user_id}, {self.user_channel_name}")
        
        #join own channel for revieving messages
        await self.channel_layer.group_add(
            self.user_channel_name, 
            self.channel_name
        )
        
        await self.accept()
        
       
    
    async def disconnect(self, close_code):
        print(f'user {self.user_id} has logged off WebSocket')
        #leave user's channel
        await self.channel_layer.group_discard(
            self.user_channel_name,
            self.channel_name
        )
        
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        reciever_user_id = text_data_json["reciever_user_id"]
        
        reciever_channel_name = f'chat_{reciever_user_id}'
        
        print(f'recieve function ran {reciever_user_id}')
        
        await self.channel_layer.group_send(
            reciever_channel_name, 
            {
                'type': 'chat.message',
                'message': message,
            }
        )
        
    async def chat_message(self, event):
        print('chat message function ran')
        message = event['message']

        await self.send(text_data=json.dumps({"message": message}))
        print("recieved message")