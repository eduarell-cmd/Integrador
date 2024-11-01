from dotenv import load_dotenv
import os

# Cargar variables desde el archivo .env
load_dotenv()

# Obtener las credenciales
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

# Imprimir las credenciales para verificar (solo durante pruebas)
print("Client ID:", client_id)
print("Client Secret:", client_secret)
