#main
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage  # Redis yerine MemoryStorage

from config import config
from handlers.upload_handler import router as upload_router
from handlers.status_handler import router as status_router
from handlers.admin_handler import router as admin_router
from handlers.dar_handler import router as dar_router   # <-- buraya ekle yeni handleri

from handlers.id_handler import router as id_router   # yeni handler

from utils.logger import setup_logger

# Logger kurulumu
setup_logger()

async def main():
    # Redis yerine MemoryStorage kullan
    storage = MemoryStorage()

    bot = Bot(
        token=config.TELEGRAM_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)

    # Router'ları yükle
    dp.include_router(upload_router)
    dp.include_router(status_router)
    dp.include_router(admin_router)
    dp.include_router(dar_router)  # <-- buraya ekle
    dp.include_router(id_router)   # yeni router ekle

    # Webhook'u kapat, polling başlat
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

bu yapı polling mi webhook mu
kısa yanıt evet/hayır
