import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SUPPLYNOTE_BASE_URL = os.getenv("SUPPLYNOTE_BASE_URL", "https://supplynote.in")
    SUPPLYNOTE_USERNAME = os.getenv("SUPPLYNOTE_USERNAME", "ginthi.ai")
    SUPPLYNOTE_PASSWORD = os.getenv("SUPPLYNOTE_PASSWORD", "user@ABC123")
    DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "./downloads")

config = Config()