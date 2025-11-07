import time, subprocess, platform, shutil, requests
from ..config import settings

BASE_URL = settings.OLLAMA_URL.rstrip("/")
API_TAGS = f"{BASE_URL}/api/tags"
_STARTED_HERE = False

def is_ollama_running() -> bool:
    try:
        r = requests.get(API_TAGS, timeout=2)
        return r.status_code == 200
    except Exception:
        return False

def start_ollama() -> bool:
    global _STARTED_HERE
    print("🚀 Ensuring Ollama service is running...")

    if is_ollama_running():
        print("✅ Ollama already running.")
        return True

    if shutil.which("brew") and platform.system() == "Darwin":
        print("🔧 Starting via Homebrew...")
        subprocess.run(["brew", "services", "start", "ollama"], check=False)
    else:
        print("⚠️ Please start manually using `ollama serve`")

    for i in range(60):
        if is_ollama_running():
            _STARTED_HERE = True
            print("✅ Ollama is ready.")
            return True
        time.sleep(2)
        if i % 10 == 0:
            print("⏳ Waiting for Ollama...")

    print("❌ Ollama did not respond.")
    return False

def stop_ollama():
    global _STARTED_HERE
    if not _STARTED_HERE:
        print("🟡 Not stopping Ollama (was not started by this process).")
        return
    print("🛑 Stopping Ollama...")
    if shutil.which("brew") and platform.system() == "Darwin":
        subprocess.run(["brew", "services", "stop", "ollama"], check=False)
        print("✅ Ollama stopped.")
    _STARTED_HERE = False