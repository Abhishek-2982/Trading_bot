# trading_bot/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from pybit.unified_trading import WebSocket

class PriceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        async def handle_message(message):
            await self.send(text_data=message)

        ws = WebSocket(testnet=True, channel_type="linear")
        ws.kline_stream(
            interval=5,
            symbol="BTCUSDT",
            callback=handle_message
        )

    async def disconnect(self, close_code):
        pass
