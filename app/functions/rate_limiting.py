from flask import request, abort
from collections import defaultdict
import time

# Registrar las IPs y sus solicitudes
ip_requests = defaultdict(list)

def limit_requests():
    ip = request.remote_addr
    now = time.time()

    # Control de solicitudes por IP (en este caso, 20 solicitudes en 10 segundos)
    ip_requests[ip].append(now)
    ip_requests[ip] = [t for t in ip_requests[ip] if now - t < 5]

    if len(ip_requests[ip]) > 10:
        abort(429)  # Too Many Requests
