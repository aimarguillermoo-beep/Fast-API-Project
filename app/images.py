# app/images.py
import os
from dotenv import load_dotenv
from imagekitio import ImageKit

load_dotenv()

# 1. Creamos la instancia totalmente vacía
# Úsalo SOLO si el código anterior falla
imagekit = ImageKit(
    os.getenv("IMAGEKIT_PUBLIC_KEY"),
    os.getenv("IMAGEKIT_PRIVATE_KEY"),
    os.getenv("IMAGEKIT_URL")
)

# 2. FORZADO: Si el error persiste, usa este bloque que asigna directo a la config:
# Dejamos esto como respaldo por si tu versión es muy estricta
# imagekit.ik_parameter.public_key = os.getenv("IMAGEKIT_PUBLIC_KEY")
# imagekit.ik_parameter.private_key = os.getenv("IMAGEKIT_PRIVATE_KEY")
# imagekit.ik_parameter.url_endpoint = os.getenv("IMAGEKIT_URL")