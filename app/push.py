# app/push_utils.py
from pywebpush import webpush, WebPushException
import json

# Claves VAPID
VAPID_PUBLIC_KEY = "BKT8mVwq7_lF2LJX0x5pK1G6xZJl3Y5D9Tt0GZocJXwQ7DdQG6GgE6kP0q1q3iP3xGzS7e5V9l7ZcRtxkZJ3t5g"
VAPID_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgK1bJvWfQv0Jt5rS1
n0O7BhdH+4mMGR9XGv0uXn1sWjGhRANCAAQpP2n1yA0ZgM1PRFhMYYKn6Up0G3qU
i+u5XWjF2Zc6dkD1/YJ9Zx+jKk+OV6bN1kVhroPkvFfRO4ZnWZ5xih/7
-----END PRIVATE KEY-----"""



# Lista temporal de suscripciones (puedes reemplazar con DB)
subscriptions = []

def add_subscription(subscription):
    """Agrega una nueva suscripción"""
    subscriptions.append(subscription)

def send_push(subscription_info, message, url="/"):
    """Envía una notificación push"""
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps({"body": message, "url": url}),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": "mailto:tu_correo@example.com"}
        )
    except WebPushException as ex:
        print("Error al enviar push:", ex)
