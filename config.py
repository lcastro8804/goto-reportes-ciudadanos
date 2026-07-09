import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
DATABASE_PATH = INSTANCE_DIR / "reportes.db"
DEFAULT_DATABASE_URI = f"sqlite:///{DATABASE_PATH.as_posix()}"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-goto-reportes")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PORT = int(os.getenv("PORT", "5055"))
