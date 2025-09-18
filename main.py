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

async def start_simple_server(port: int):
    """Render için basit bir HTTP sunucusu başlat"""
    def handle_request(conn):
        try:
            conn.recv(1024)  # İsteği al (kullanmasak da)
            response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nBot is running"
            conn.send(response)
        except Exception as e:
            print(f"HTTP hatası: {e}")
        finally:
            conn.close()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', port))
    sock.listen(5)
    print(f"🔄 Health check sunucusu {port} portunda başlatıldı")
    
    return sock

async def main():
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
    
    # Render için health check sunucusu başlat
    server_socket = await start_simple_server(config.PORT)
    
    try:
        # Webhook'u kapat, polling başlat
        await bot.delete_webhook(drop_pending_updates=True)
        print("🤖 Bot polling başlatılıyor...")
        
        # Bot'u ayrı bir task'ta başlat
        bot_task = asyncio.create_task(dp.start_polling(bot))
        
        # Hem botu hem de health check'i çalıştır
        await asyncio.gather(bot_task)
        
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        server_socket.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
