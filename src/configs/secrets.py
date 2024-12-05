import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL_VERIFICATION = os.getenv("DATABASE_URL_VERIFICATION")
