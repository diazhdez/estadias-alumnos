from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

# Generar la clave privada (P-256)
private_key = ec.generate_private_key(ec.SECP256R1())

# Exportar clave privada en formato base64 URL-safe
private_key_bytes = private_key.private_numbers().private_value.to_bytes(32, 'big')
private_key_b64 = base64.urlsafe_b64encode(private_key_bytes).decode('utf-8').rstrip("=")

# Generar la clave pública (punto en curva)
public_key = private_key.public_key().public_numbers()
x = public_key.x.to_bytes(32, 'big')
y = public_key.y.to_bytes(32, 'big')
public_key_bytes = b'\x04' + x + y
public_key_b64 = base64.urlsafe_b64encode(public_key_bytes).decode('utf-8').rstrip("=")

print("Public key:", public_key_b64)
print("Private key:", private_key_b64)
