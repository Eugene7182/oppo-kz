from pydantic_settings import BaseSettings

class FeatureFlags(BaseSettings):
    # Гео/селфи выключены по умолчанию (можно включить ENV-ами)
    ENABLE_GEO_CHECKIN: bool = False
    ENABLE_SELFIE_CHECKIN: bool = False
    # AI-инсайты включены по умолчанию
    ENABLE_AI_INSIGHTS: bool = True
    # Фото-напоминания пушем (только для супервизоров) — включаются на уровне админа
    ENABLE_PHOTO_REMINDERS: bool = False
    TIMEZONE: str = "Asia/Almaty"

    class Config:
        env_file = ".env"
        case_sensitive = False
