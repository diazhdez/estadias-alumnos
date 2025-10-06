from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

# Crea la clave privada
private_key = ec.generate_private_key(ec.SECP256R1())
private_pem = private_key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption()
)

# Deriva la clave pública
public_key = private_key.public_key()
public_der = public_key.public_bytes(
    serialization.Encoding.DER,
    serialization.PublicFormat.SubjectPublicKeyInfo
)

# Convierte a Base64 URL safe para JS
public_b64url = base64.urlsafe_b64encode(public_der).decode('utf-8').rstrip("=")

print("PRIVATE KEY (Python pywebpush):\n", private_pem.decode())
print("PUBLIC KEY (JS applicationServerKey):\n", public_b64url)
