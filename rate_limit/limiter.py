from fastapi import HTTPException, Request
from .redis_client import redis_client


async def rate_limit(
    request: Request,
    limit: int = 5,
    window: int = 60
):
    client_ip = request.client.host
    endpoint = request.url.path

    key = f"rate_limit:{client_ip}:{endpoint}"

    current_count = await redis_client.incr(key)

    if current_count == 1:
        await redis_client.expire(key, window)

    if current_count > limit:
        ttl = await redis_client.ttl(key)

        raise HTTPException(
            status_code=429,
            detail={
                "message": "Rate limit exceeded. Try again later.",
                "limit": limit,
                "window_seconds": window,
                "retry_after_seconds": ttl
            }
        )

    return current_count