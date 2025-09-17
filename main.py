import asyncio
import json
import websockets
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoinbaseWebSocketClient:
    def __init__(self):
        self.uri = "wss://ws-feed.exchange.coinbase.com"
        self.websocket = None

    async def connect(self):
        """Connect to the Coinbase WebSocket feed"""
        try:
            logger.info(f"Connecting to {self.uri}")
            self.websocket = await websockets.connect(self.uri)
            logger.info("Successfully connected to Coinbase WebSocket")

            # Subscribe to ticker data for BTC-USD (you can modify this)
            subscribe_message = {
                "type": "subscribe",
                "product_ids": ["BTC-USD", "ETH-USD"],
                "channels": ["ticker"],
            }

            await self.websocket.send(json.dumps(subscribe_message))
            logger.info("Subscription message sent")

        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise

    async def listen(self):
        """Listen for messages from the WebSocket"""
        if not self.websocket:
            raise Exception("WebSocket not connected. Call connect() first.")

        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {e}")
                    print(f"Raw message: {message}")

        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error while listening: {e}")

    async def handle_message(self, data):
        """Handle incoming WebSocket messages"""
        message_type = data.get("type", "unknown")

        if message_type == "subscriptions":
            logger.info("Subscription confirmed")
            print(f"Subscribed to: {json.dumps(data, indent=2)}")

        elif message_type == "ticker":
            # Print ticker data
            product_id = data.get("product_id", "N/A")
            price = data.get("price", "N/A")
            time = data.get("time", "N/A")

            print(f"[{time}] {product_id}: ${price}")

        elif message_type == "error":
            logger.error(f"WebSocket error: {data}")

        else:
            # Print all other messages
            print(f"Message type: {message_type}")
            print(json.dumps(data, indent=2))

    async def close(self):
        """Close the WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            logger.info("WebSocket connection closed")


async def main():
    """Main function to run the WebSocket client"""
    client = CoinbaseWebSocketClient()

    try:
        await client.connect()
        await client.listen()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    # Install required packages first:
    # pip install websockets

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
