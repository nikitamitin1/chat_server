import json, asyncio, logging
from aiokafka import AIOKafkaConsumer
from firebase_admin import messaging, initialize_app, credentials
from infrastructure.db.session_factory import session_factory
from infrastructure.persistence.sqlalchemy.repos import SqlNotificationRepository

initialize_app(credentials.ApplicationDefault())
log = logging.getLogger("push-worker")


async def send_push(device_token: str, title: str, body: str):
    msg = messaging.Message(notification=messaging.Notification(title, body),
                            token=device_token)
    await asyncio.to_thread(messaging.send, msg)   # firebase call is blocking


async def run_push_worker():
    consumer = AIOKafkaConsumer(
        "notifications",
        bootstrap_servers="localhost:9092",
        value_deserializer=lambda b: json.loads(b.decode()),
        group_id="push-worker",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            notif = msg.value                      # NotificationCreated payload
            async with session_factory() as sess:
                repo = SqlNotificationRepository(sess)
                # fetch device tokens, user prefs …
            await send_push(notif["device_token"],
                            notif["title"], notif["body"])
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(run_push_worker())
