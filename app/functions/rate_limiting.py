from flask import render_template, request, abort
from collections import defaultdict
import time

# Registrar las IPs y sus solicitudes
ip_requests = defaultdict(list)
ip_blocked = defaultdict(float)  # Almacena el tiempo en que la IP fue bloqueada



def limit_requests():
    ip = request.remote_addr
    now = time.time()

    # Verificar si la IP está bloqueada
    if ip in ip_blocked and now - ip_blocked[ip] < BLOCK_TIME:
        # Si la IP está bloqueada, mostrar la página de error
        return render_template("error_page_copy.html"), 429

    # Si la IP no está bloqueada, controlar las solicitudes
    ip_requests[ip].append(now)
    ip_requests[ip] = [t for t in ip_requests[ip] if now - t < 5]  # Control de solicitudes en 5 segundos

    if len(ip_requests[ip]) > 20:  # Si supera el límite de 10 solicitudes en 5 segundos
        # Bloquear la IP durante 20 minutos
        ip_blocked[ip] = now
        return render_template("error_page.html"), 429  # Redirigir a la página de error

