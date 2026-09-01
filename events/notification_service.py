import json
from datetime import datetime

LOG_FILE = "event_logs.log"


async def process_notification(event: dict):
    event_type = event.get("event_type")
    user_id = event.get("user_id")
    event_id = event.get("event_id")

    data = event.get("data", {})

    if isinstance(data, str):
        data = json.loads(data)

    messages = {
        "account_created": "Welcome! Your account has been created.",
        "order_placed": "Your order has been placed successfully.",
        "status_changed": "Your order status has been updated."
    }

    notification = messages.get(
        event_type,
        f"Notification received for event: {event_type}"
    )

    log_entry = (
        f"{datetime.now().isoformat()} | "
        f"event_id={event_id} | "
        f"user_id={user_id} | "
        f"type={event_type} | "
        f"notification={notification}"
    )

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(log_entry + "\n")

    print(f"[NOTIFICATION] {notification}")

    return notification