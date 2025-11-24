from cryptography.fernet import Fernet

# Generar nueva clave
key = Fernet.generate_key()
print("ENCRYPTION_KEY=" + key.decode())
print("\nAgrega esta línea a tu archivo .env")
