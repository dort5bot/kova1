import asyncio
import socket
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

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
        # İsteği oku (ama kullanma)
        await reader.read(1024)
        
        # Basit HTTP yanıtı
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
    server = await asyncio.start_server(
        handle_health_check, 
        '0.0.0.0', 
        port
    )
    
    print(f"✅ Health check sunucusu {port} portunda başlatıldı")
    return server

async def main():
    # Önce bot token kontrolü
    if not config.TELEGRAM_TOKEN:
        print("❌ HATA: Bot token bulunamadı!")
        print("Lütfen BOT_TOKEN environment variable'ını kontrol edin")
        return

    storage = MemoryStorage()

    # Bot oluşturma
    bot = Bot(
        token=config.TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
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
        # Health check sunucusunu başlat
        health_server = await start_health_check_server(config.PORT)
        
        # Webhook'u kapat, polling başlat
        await bot.delete_webhook(drop_pending_updates=True)
        print("🤖 Bot polling başlatılıyor...")
        
        # Hem health check sunucusunu hem de botu çalıştır
        async with health_server:
            # Health check sunucusunu arka planda çalıştır
            health_task = asyncio.create_task(health_server.serve_forever())
            
            # Botu çalıştır
            try:
                await dp.start_polling(bot)
            finally:
                # Bot durduğunda health task'ı iptal et
                health_task.cancel()
                try:
                    await health_task
                except asyncio.CancelledError:
                    pass
                
    except Exception as e:
        print(f"❌ Ana hata: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
