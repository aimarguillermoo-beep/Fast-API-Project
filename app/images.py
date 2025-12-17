# app/images.py
import os
from pathlib import Path
from dotenv import load_dotenv
from imagekitio import ImageKit

# Load .env from the app directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize ImageKit with the new v5.0.0 API
# Note: v5.0.0 uses the default base_url (https://api.imagekit.io)
# Only private_key is needed for initialization
# public_key is passed as a parameter to upload() method
imagekit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY")
)