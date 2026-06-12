from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[1]

APP_NAME = os.getenv("APP_NAME", "OpsPilot")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:3b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

DATA_DIR = ROOT_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"
LOGS_DIR = DATA_DIR / "logs"

CHROMA_DIR = ROOT_DIR / os.getenv("CHROMA_DIR", ".chroma")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "opspilot_runbooks")

TOP_K = int(os.getenv("TOP_K", "4"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.35"))