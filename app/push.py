# app/push_utils.py
from pywebpush import webpush, WebPushException
import json

# Claves VAPID
VAPID_PUBLIC_KEY = "BCzzEJZv7f86NFxKGVrExCfqYgQ0ld0-nxTZ9WAsRhbdekEC_Zk8o_fzGS4PlGFJyNlutmqdurS4T4Jobsh0yPk"
VAPID_PRIVATE_KEY = "1Kri_Mfdii2cjpJ06FNHCEJuV4YyCi5ZFLC0R9wH9KU"
VAPID_CLAIMS = {
    "sub": "mailto:javiertoledo455@gmail.com"  # pon tu correo aquí, importante para VAPID
}



# Lista temporal de suscripciones (puedes reemplazar con DB)
subscriptions = []

def add_subscription(subscription):
    """Agrega una nueva suscripción"""
    subscriptions.append(subscription)

def send_notification(subscription_info, message):
    webpush(
        subscription_info=subscription_info,
        data=message,
        vapid_private_key=VAPID_PRIVATE_KEY,
        vapid_claims=VAPID_CLAIMS
    )
