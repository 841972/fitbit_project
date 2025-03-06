# encryption.py
from cryptography.fernet import Fernet
import base64
from dotenv import load_dotenv
import os

load_dotenv()

# Generar una clave secreta (debe ser la misma para cifrar y descifrar)
SECRET_KEY = os.getenv('ENCRYPTION_KEY')

# Asegúrate de que la clave tenga 32 bytes
if len(SECRET_KEY) != 32:
    raise ValueError("La clave de cifrado debe tener 32 bytes.")

# Convertir la clave a formato base64 para Fernet
fernet_key = base64.urlsafe_b64encode(SECRET_KEY.encode())
cipher_suite = Fernet(fernet_key)

def encrypt_token(token):
    """
    Cifra un token usando AES.
    """
    if not token:
        return None
    return cipher_suite.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token):
    """
    Descifra un token usando AES.
    """
    if not encrypted_token:
        return None
    return cipher_suite.decrypt(encrypted_token.encode()).decode()
