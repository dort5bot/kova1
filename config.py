import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
env_path = Path('.') / '.env'
logging.info(f".env dosya yolu: {env_path.absolute()}")
logging.info(f".env dosyası var mı: {env_path.exists()}")

load_dotenv()

# Debug amaçlı bazı env değişkenlerini göster
logging.info("Mevcut env değişkenleri:")
for key in ['TELEGRAM_TOKEN', 'ADMIN_CHAT_IDS', 'SMTP_USERNAME']:
    value = os.getenv(key)
    if value:
        logging.info(f"  {key}: {value}")
    else:
        logging.warning(f"  {key}: TANIMSIZ")


@dataclass
class Config:
    # -----------------------------
    # Temel Bot Ayarları
    # -----------------------------
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")

    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    ADMIN_CHAT_IDS: list[int] = field(default_factory=list)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # -----------------------------
    # Webhook / Polling Ayarları
    # -----------------------------
    USE_WEBHOOK: bool = False
    WEBHOOK_URL: str = ""
    WEBHOOK_SECRET: str = ""
    PORT: int = 3000  # Varsayılan, sonra __post_init__ içinde güncellenir

    def __post_init__(self):
        # -----------------------------
        # Admin Chat ID'leri Yükle
        # -----------------------------
        admin_ids = os.getenv("ADMIN_CHAT_IDS", "")
        logging.info(f"ADMIN_CHAT_IDS raw değer: '{admin_ids}'")
        logging.info(f"ADMIN_CHAT_IDS type: {type(admin_ids)}")

        self.ADMIN_CHAT_IDS = []
        if admin_ids and admin_ids.strip():
            try:
                cleaned = admin_ids.strip()
                if "," in cleaned:
                    ids_list = [int(id_str.strip()) for id_str in cleaned.split(",")]
                else:
                    ids_list = [int(cleaned)]

                self.ADMIN_CHAT_IDS = ids_list
                logging.info(f"✅ Yüklenen Admin ID'leri: {self.ADMIN_CHAT_IDS}")
            except ValueError as e:
                logging.error(f"❌ HATA: Admin ID dönüşüm hatası: {e}")
                logging.error(f"❌ Hatalı değer: '{admin_ids}'")
        else:
            logging.warning("⚠️ ADMIN_CHAT_IDS boş veya tanımlanmamış")

        # -----------------------------
        # Webhook Ayarları
        # -----------------------------
        self.USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"
        self.WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
        self.WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

        # -----------------------------
        # PORT'u ortamdan oku (Render uyumlu)
        # PORT YAZMA! Render bunu kendi belirliyor!
        # -----------------------------
        try:
            port_str = os.getenv("PORT", "3000")
            self.PORT = int(port_str)
            logging.info(f"✅ PORT değeri yüklendi: {self.PORT}")
        except ValueError:
            logging.warning(f"⚠️ Geçersiz PORT değeri: {os.getenv('PORT')}, varsayılan 3000 kullanılacak")
            self.PORT = 3000

        # -----------------------------
        # Veri klasörlerini hazırla
        # -----------------------------
        self.DATA_DIR = Path(__file__).parent / "data"
        self.INPUT_DIR = self.DATA_DIR / "input"
        self.OUTPUT_DIR = self.DATA_DIR / "output"
        self.GROUPS_DIR = self.DATA_DIR / "groups"
        self.LOGS_DIR = self.DATA_DIR / "logs"

        for directory in [
            self.DATA_DIR,
            self.INPUT_DIR,
            self.OUTPUT_DIR,
            self.GROUPS_DIR,
            self.LOGS_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


# Config objesi
config = Config()
