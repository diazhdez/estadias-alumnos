from flask import Blueprint, request, jsonify
from app.push import add_subscription, subscriptions, send_notification

bp = Blueprint("notificaciones", __name__)

@bp.route('/subscribe', methods=['POST'])
def subscribe():
    subscription = request.json
    print("Nueva suscripción recibida:", subscription)  # 👈 LOG
    add_subscription(subscription)
    return jsonify({"success": True})


