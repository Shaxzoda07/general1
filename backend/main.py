import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from config import BOT_TOKEN, BASE_URL, WEBHOOK_SECRET, CORS_ORIGINS
from database import engine, Base
import models

from routers import users, tasks

logger = logging.getLogger("uvicorn.error")

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Bot webhook rejimida ishlaydi: Render bepul rejada servis "uxlab qolsa"
    # ham, Telegram xabar yuborganda servis uyg'onadi.
    if BOT_TOKEN and BASE_URL:
        from bot import bot

        try:
            await bot.set_webhook(
                f"{BASE_URL}/webhook",
                secret_token=WEBHOOK_SECRET,
                drop_pending_updates=True
            )
            logger.info("Telegram webhook o'rnatildi: %s/webhook", BASE_URL)
        except Exception:
            logger.exception("Webhook o'rnatib bo'lmadi")
    elif not BOT_TOKEN:
        logger.warning("BOT_TOKEN berilmagan: Telegram bot o'chirilgan, faqat API ishlaydi")

    yield

    if BOT_TOKEN:
        from bot import bot

        await bot.session.close()


app = FastAPI(
    title="Telegram Task Manager API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(tasks.router)


@app.get("/")
def home():
    return {
        "status": "success",
        "message": "Task Manager API is running"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None)
):
    if not BOT_TOKEN:
        raise HTTPException(404, "Bot disabled")

    if x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(403, "Forbidden")

    from aiogram.types import Update
    from bot import bot, dp

    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)

    return {"ok": True}
