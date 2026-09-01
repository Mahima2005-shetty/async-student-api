import asyncio
from redis.asyncio import Redis

from events.producer import STREAM_NAME
from events.notification_service import process_notification


GROUP_NAME = "notification_group"
CONSUMER_NAME = "notification_consumer"

PROCESSED_PREFIX = "processed_event:"
RETRY_PREFIX = "retry_event:"

MAX_RETRIES = 3
RETRY_DELAY = 2


async def create_consumer_group(redis: Redis):
    try:
        await redis.xgroup_create(
            STREAM_NAME,
            GROUP_NAME,
            id="0",
            mkstream=True
        )

        print("Consumer group created.")

    except Exception as error:

        if "BUSYGROUP" in str(error):
            print("Consumer group already exists.")

        else:
            print(f"Consumer group error: {error}")


async def process_message(redis: Redis, message_id: str, fields: dict):

    event_id = fields.get("event_id")

    if not event_id:
        print("[ERROR] Event does not contain event_id.")

        await redis.xack(
            STREAM_NAME,
            GROUP_NAME,
            message_id
        )

        return

    processed_key = PROCESSED_PREFIX + event_id
    retry_key = RETRY_PREFIX + event_id

    # Check idempotency
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

        return

    event = {
        "event_id": fields.get("event_id"),
        "event_type": fields.get("event_type"),
        "user_id": fields.get("user_id"),
        "data": fields.get("data")
    }

    retry_count = int(
        await redis.get(retry_key) or 0
    )

    while retry_count < MAX_RETRIES:

        try:

            await process_notification(event)

            # Mark event as successfully processed
            await redis.set(
                processed_key,
                "1",
                ex=86400
            )

            # Remove retry counter
            await redis.delete(retry_key)

            # Acknowledge Redis Stream message
            await redis.xack(
                STREAM_NAME,
                GROUP_NAME,
                message_id
            )

            print(
                f"[SUCCESS] Event {event_id} processed."
            )

            return

        except Exception as error:

            retry_count += 1

            await redis.set(
                retry_key,
                str(retry_count),
                ex=86400
            )

            print(
                f"[RETRY] Event {event_id} "
                f"attempt {retry_count}"
            )

            print(
                f"[ERROR] {error}"
            )

            if retry_count >= MAX_RETRIES:

                print(
                    f"[FAILED] Event {event_id} "
                    f"failed after {MAX_RETRIES} attempts."
                )

                # Acknowledge the failed message
                await redis.xack(
                    STREAM_NAME,
                    GROUP_NAME,
                    message_id
                )

                return

            await asyncio.sleep(RETRY_DELAY)


async def consume_events(redis: Redis):

    await create_consumer_group(redis)

    print("Event consumer started...")

    while True:

        try:

            messages = await redis.xreadgroup(
                GROUP_NAME,
                CONSUMER_NAME,
                {
                    STREAM_NAME: ">"
                },
                count=1,
                block=5000
            )

            if not messages:
                continue

            for stream, entries in messages:

                for message_id, fields in entries:

                    await process_message(
                        redis,
                        message_id,
                        fields
                    )

        except asyncio.CancelledError:

            print("Consumer stopped.")
            break

        except Exception as error:

            print(
                f"[CONSUMER ERROR] {error}"
            )

            await asyncio.sleep(2)


async def main():

    redis = Redis(
        host="localhost",
        port=6379,
        decode_responses=True
    )

    try:

        await redis.ping()

        print("Redis connection successful!")

        await consume_events(redis)

    finally:

        await redis.aclose()


if __name__ == "__main__":
    asyncio.run(main())