#main.py
#kova
#.env → USE_WEBHOOK=true/false ile mod seçiliyor.
import asyncio
import os
import socket
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

from config import config
from handlers.upload_handler import router as upload_router
from handlers.status_handler import router as status_router
from handlers.admin_handler import router as admin_router
from handlers.dar_handler import router as dar_router
from handlers.id_handler import router as id_router
from handlers.json_handler import router as json_router
from handlers.buttons.button_handler import router as button_router

from utils.logger import setup_logger

# Logger kurulumu
setup_logger()


async def handle_health_check(reader, writer):
    """Asenkron health check handler"""
    try:
        await reader.read(1024)  # isteği oku
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nBot is running"
        writer.write(response.encode())
        await writer.drain()
    except Exception as e:
        print(f"Health check hatası: {e}")
    finally:
        writer.close()
        await writer.wait_closed()


async def start_health_check_server(port: int):
    """Asenkron health check sunucusu başlat"""
    server = await asyncio.start_server(handle_health_check, "0.0.0.0", port)
    print(f"✅ Health check sunucusu {port} portunda başlatıldı")
    return server


# -------------------------------
# Webhook mode için aiohttp server + health check endpoint
#hem sağlık kontrol endpoint’ini aynı app içinde, aynı portta barındır
# -------------------------------
async def webhook_handler(request: web.Request):
    """Telegram'dan gelen update'leri aiogram'a aktarır"""
    dp: Dispatcher = request.app["dp"]
    bot: Bot = request.app["bot"]
    try:
        update = await request.json()
        await dp.feed_webhook_update(bot, update, request)
        return web.Response(text="ok")
    except Exception as e:
        print(f"Webhook hata: {e}")
        return web.Response(status=500, text="error")

async def health_check_handler(request: web.Request):
    """Sağlık kontrol endpoint"""
    return web.Response(text="Bot is running")

async def start_webhook(bot: Bot, dp: Dispatcher):
    """Webhook mode başlatıcı, aynı app içinde health check ile"""
    app = web.Application()
    app["dp"] = dp
    app["bot"] = bot

    # Webhook endpoint -> /webhook/<BOT_TOKEN>
    path = f"/webhook/{config.TELEGRAM_TOKEN}"
    app.router.add_post(path, webhook_handler)

    # Sağlık kontrol endpoint -> /health
    app.router.add_get("/health", health_check_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", config.PORT)
    print(f"🌐 Webhook ve health check sunucusu {config.PORT} portunda dinleniyor ({path} ve /health)")
    await site.start()

    # Telegram'a webhook bildir
    await bot.set_webhook(
        url=f"{config.WEBHOOK_URL}{path}",
        secret_token=config.WEBHOOK_SECRET or None,
        drop_pending_updates=True,
    )

# -------------------------------
# Main
# -------------------------------
# main.py'de main fonksiyonunu güncelle
async def main():
    if not config.TELEGRAM_TOKEN:
        print("❌ HATA: Bot token bulunamadı!")
        return

    storage = MemoryStorage()

    bot = Bot(
        token=config.TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)

    # Router'ları yükle
    dp.include_router(upload_router)
    dp.include_router(status_router)
    dp.include_router(admin_router)
    dp.include_router(dar_router)
    dp.include_router(id_router)
    dp.include_router(json_router)
    dp.include_router(button_router)

    try:
        if config.USE_WEBHOOK:
            # Webhook modu - Render için bu modu kullan
            print("🚀 Webhook modu başlatılıyor...")
            print(f"🌐 Port: {config.PORT}")
            
            # Webhook sunucusunu başlat
            await start_webhook(bot, dp)
            
            # Health check sunucusunu da aynı portta çalıştırıyoruz
            # Bu satırı kaldırın çünkü start_webhook içinde zaten health check var
            # server = await start_health_check_server(config.PORT)
            
            print(f"✅ Bot {config.PORT} portunda dinlemeye başladı")
            
            # Sonsuza kadar bekle
            await asyncio.Event().wait()
        else:
            # Polling modu - Render'da bu mod çalışmaz!
            print("🤖 Polling modu başlatılıyor...")
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)

    except Exception as e:
        print(f"❌ Ana hata: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())


