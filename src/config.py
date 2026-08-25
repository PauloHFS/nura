import os

GROCY_API_URL = os.getenv("GROCY_API_URL", os.getenv("GROCY_BASE_URL", "http://localhost:8080/api"))
GROCY_API_KEY = os.getenv("GROCY_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nura.db")
CHROMA_PERSIST_PATH = os.getenv("CHROMA_PERSIST_PATH", "./chroma_data")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
