import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Settings:

    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "codellama")
    
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    CHAR_LIMIT = int(os.getenv("CHAR_LIMIT", "30000"))
    USE_OLLAMA = os.getenv("USE_OLLAMA", "0") == "1"
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output").strip()
    OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output")).expanduser()
    
    CSS_DIR = Path(os.getenv("CSS_FOLDER", "")).expanduser()
   
    CSS_FOLDER = os.getenv("CSS_FOLDER", "").strip()
    CSS_ORDER_RAW = os.getenv("CSS_ORDER", "").strip()
    CSS_MODE = os.getenv("CSS_MODE", "order").strip().lower()  # "all" or "order"
   
    # Feature toggles
    USE_REFACTOR = os.getenv("USE_REFACTOR", "1") in ["1", "true", "True"]
    USE_AUDIT = os.getenv("USE_AUDIT", "1") in ["1", "true", "True"]
    USE_GRAPH_ANALYSIS = os.getenv("USE_GRAPH_ANALYSIS", "1") in ["1", "true", "True"]

    TARGET_URL = os.getenv("TARGET_URL", "").strip() or None

    
    @property
    def CSS_DIR(self) -> Path:
        if not self.CSS_FOLDER:
            raise RuntimeError("❌ No CSS_FOLDER defined in .env")
        path = Path(self.CSS_FOLDER)
        if not path.exists():
            raise RuntimeError(f"❌ CSS_FOLDER does not exist: {path}")
        return path

settings = Settings()