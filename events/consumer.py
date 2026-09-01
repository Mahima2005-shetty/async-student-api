import asyncio
from redis.asyncio import Redis

from events.producer import STREAM_NAME
from events.notification_service import process_notification

GROUP_NAME = "notification_group"
CONSUMER_NAME = "notification_consumer"

PROCESSED_PREFIX = "processed_event:"
RETRY_PREFIX = "retry_event:"


async def create_consumer_group(redis: Redis):
    try:
        await redis.xgroup_create(
            STREAM_NAME,
            GROUP_NAME,
            id="0",
            mkstream=True
        )
        print("Consumer group created.")

    except Exception as e:
        if "BUSYGROUP" not in str(e):
            print(f"Consumer group error: {e}")


async def consume_events(redis: Redis):
    await create_consumer_group(redis)

    print("Event consumer started...")

    while True:
        try:
            messages = await redis.xreadgroup(
                GROUP_NAME,
                CONSUMER_NAME,
                {STREAM_NAME: ">"},
                count=1,
                block=5000
            )

            if not messages:
                continue

            for stream, entries in messages:

                for message_id, fields in entries:

                    event_id = fields.get("event_id")

                    processed_key = PROCESSED_PREFIX + event_id

                    already_processed = await redis.get(processed_key)

                    if already_processed:
                        print(
                            f"[DUPLICATE] Event {event_id} already processed."
                        )

                        await redis.xack(
                            STREAM_NAME,
                            GROUP_NAME,
                            message_id
                        )

                        continue

                    try:
                        event = {
                            "event_id": fields.get("event_id"),
                            "event_type": fields.get("event_type"),
                            "user_id": fields.get("user_id"),
                            "data": fields.get("data")
                        }

                        await process_notification(event)

                        await redis.set(
                            processed_key,
                            "1",
                            ex=86400
                        )

                        await redis.xack(
                            STREAM_NAME,
                            GROUP_NAME,
                            message_id
                        )

                        print(
                            f"[SUCCESS] Event {event_id} processed."
                        )

                    except Exception as error:

                        retry_key = RETRY_PREFIX + event_id

                        retry_count = await redis.incr(retry_key)

                        print(
                            f"[RETRY] Event {event_id} "
                            f"attempt {retry_count}"
                        )

                        if retry_count >= 3:
                            print(
                                f"[FAILED] Event {event_id} "
                                f"failed after 3 attempts."
                            )

                            await redis.xack(
                                STREAM_NAME,
                                GROUP_NAME,
                                message_id
                            )

        except asyncio.CancelledError:
            print("Consumer stopped.")
            break

        except Exception as error:
            print(f"[CONSUMER ERROR] {error}")
            await asyncio.sleep(2)