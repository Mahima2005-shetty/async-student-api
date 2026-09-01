import json
import uuid
from redis.asyncio import Redis

STREAM_NAME = "application_events"


async def publish_event(
    redis: Redis,
    event_type: str,
    user_id: int,
    data: dict,
    event_id: str | None = None
):
    event_id = event_id or str(uuid.uuid4())

    event = {
        "event_id": event_id,
        "event_type": event_type,
        "user_id": str(user_id),
        "data": json.dumps(data)
    }

    message_id = await redis.xadd(
        STREAM_NAME,
        event
    )

    return {
        "message_id": message_id,
        "event_id": event_id,
        "status": "published"
    }