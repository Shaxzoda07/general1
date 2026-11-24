import hashlib
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")

# Render beradigan DATABASE_URL (PostgreSQL). Lokal ishlaganda SQLite ishlatiladi.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./task_manager.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Render har bir web service uchun RENDER_EXTERNAL_URL ni o'zi beradi
BASE_URL = (os.getenv("WEBHOOK_BASE_URL") or os.getenv("RENDER_EXTERNAL_URL", "")).rstrip("/")

# Telegram webhook maxfiy kaliti (bot tokenidan hosil qilinadi, alohida o'zgaruvchi kerak emas)
WEBHOOK_SECRET = hashlib.sha256(BOT_TOKEN.encode()).hexdigest() if BOT_TOKEN else ""

# Frontend manzil(lar)i, vergul bilan: https://a.onrender.com,https://b.com
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
