# app/push_utils.py
from pywebpush import webpush, WebPushException
import json

# Claves VAPID
VAPID_PUBLIC_KEY = "BMU4Eo9PZSY1D6w52Weo7xZB6VfPhwCjv8kVjY7NheHGgU4yqFvfr2Hfl1nPo1UOpE8oBz"
VAPID_PRIVATE_KEY = "YKyn_3fYgsvhZP7dO6OSVtZ9QnLvn9G1S1MuHgZCwUc"



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
