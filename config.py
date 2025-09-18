# config.py
import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Önce dotenv'i yükle
env_path = Path('.') / '.env'
logging.info(f".env dosya yolu: {env_path.absolute()}")
logging.info(f".env dosyası var mı: {env_path.exists()}")

load_dotenv()

# Tüm env değişkenlerini debug için göster
logging.info("Mevcut env değişkenleri:")
for key in ['BOT_TOKEN', 'ADMIN_CHAT_IDS', 'SMTP_USERNAME']:
    value = os.getenv(key)
    if value:
        logging.info(f"  {key}: {value}")
    else:
        logging.warning(f"  {key}: TANIMSIZ")

@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    TELEGRAM_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    ADMIN_CHAT_IDS: list[int] = field(default_factory=list)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Render için port ayarı
    PORT: int = int(os.getenv("PORT", 10000))

    def __post_init__(self):
        # ADMIN_CHAT_IDS'i yükle - GELİŞMİŞ DEBUG
        admin_ids = os.getenv("ADMIN_CHAT_IDS", "")
        logging.info(f"ADMIN_CHAT_IDS raw değer: '{admin_ids}'")
        logging.info(f"ADMIN_CHAT_IDS type: {type(admin_ids)}")
        
        self.ADMIN_CHAT_IDS = []
        if admin_ids and admin_ids.strip():
            try:
                # Çeşitli formatları destekle
                cleaned = admin_ids.strip()
                if ',' in cleaned:
                    ids_list = [int(id_str.strip()) for id_str in cleaned.split(',')]
                else:
                    ids_list = [int(cleaned)]
                
                self.ADMIN_CHAT_IDS = ids_list
                logging.info(f"✅ Yüklenen Admin ID'leri: {self.ADMIN_CHAT_IDS}")
            except ValueError as e:
                logging.error(f"❌ HATA: Admin ID dönüşüm hatası: {e}")
                logging.error(f"❌ Hatalı değer: '{admin_ids}'")
        else:
            logging.warning("⚠️ ADMIN_CHAT_IDS boş veya tanımlanmamış")
            
        # Diğer ayarlar...
        self.DATA_DIR = Path(__file__).parent / "data"
        self.INPUT_DIR = self.DATA_DIR / "input"
        self.OUTPUT_DIR = self.DATA_DIR / "output"
        self.GROUPS_DIR = self.DATA_DIR / "groups"
        self.LOGS_DIR = self.DATA_DIR / "logs"

        for directory in [self.DATA_DIR, self.INPUT_DIR, self.OUTPUT_DIR, self.GROUPS_DIR, self.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

config = Config()
