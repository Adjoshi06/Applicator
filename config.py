"""Configuration management for the job application assistant."""
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


class Config:
    """Application configuration."""
    
    # Google APIs
    GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
    GOOGLE_DRIVE_RESUME_ID = os.getenv("GOOGLE_DRIVE_RESUME_ID", "")
    
    # User preferences
    USER_PREFERENCES = os.getenv("USER_PREFERENCES", "").split(",") if os.getenv("USER_PREFERENCES") else []
    USER_LOCATION = os.getenv("USER_LOCATION", "")
    MIN_SCORE_FOR_RESEARCH = int(os.getenv("MIN_SCORE_FOR_RESEARCH", "70"))
    MIN_SCORE_FOR_NOTIFICATION = int(os.getenv("MIN_SCORE_FOR_NOTIFICATION", "80"))
    
    # Ollama
    OLLAMA_MODEL = "llama3.1:8b"
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Storage
    DATA_DIR = Path("jobs")
    CHROMA_DIR = Path("chroma_db")
    RESUME_CACHE_FILE = Path("resume_cache.json")
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.CHROMA_DIR.mkdir(exist_ok=True)

