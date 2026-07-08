from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()

print("Username:", os.getenv("COPERNICUS_USERNAME"))
print("Password Loaded:", os.getenv("COPERNICUS_PASSWORD") is not None)