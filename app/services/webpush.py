import asyncio
import json
from datetime import datetime, timezone

from pywebpush import webpush, WebPushException

from app.database import (get_vapid_keys, get_web_subscriptions_with_device_id, remove_device)


async def push_web_call_alert(username: str, phone_number: str, payload: dict = None):
    subscriptions = get_web_subscriptions_with_device_id(username)
    data = {"type": "call", "phone_number": phone_number}
    if payload and payload.get("type") == "missed":
        data["type"] = "missed-call"
    title = "Missed Call" if data["type"] == "missed-call" else "Incoming Call"
    return await asyncio.gather(*[
        send_web_push(username, device_id, subscription, title, phone_number, data)
        for device_id, subscription in subscriptions.items()
    ])

async def push_web_sms_alert(
        username: str, phone_number: str, message_body: str, from_device: str = None, forward_to_gsm: bool = False):
    subscriptions = get_web_subscriptions_with_device_id(username)
    if from_device:
        subscriptions = {k: v for k, v in subscriptions.items() if k != from_device}
    data = {"type": "sms", "phone_number": phone_number, "body": message_body, "forward_to_gsm": str(forward_to_gsm)}
    title = f"New SMS from {phone_number}"
    return await asyncio.gather(*[
        send_web_push(username, device_id, subscription, title, message_body, data)
        for device_id, subscription in subscriptions.items()
    ])

async def send_web_push(username: str, device_id: str, subscription: dict, title: str, body: str, data: dict) -> dict:
    data = {**data, "timestamp": datetime.now(timezone.utc).isoformat(timespec='seconds')}
    notification = {"title": title, "body": body, "data": data}
    vapid_keys = get_vapid_keys()

    try:
        response = await asyncio.to_thread(
            webpush,
            subscription_info=subscription,
            data=json.dumps(notification),
            vapid_private_key=vapid_keys["private_key"],
            vapid_claims={"sub": vapid_keys["subject"]},
        )
        return {"status": response.status_code, "data": {"message": "Push sent"}}
    except WebPushException as exc:
        status = exc.response.status_code if exc.response is not None else 500
        if status in (404, 410):
            remove_device(username, device_id)
        return {"status": status, "data": {"error": str(exc)}}
