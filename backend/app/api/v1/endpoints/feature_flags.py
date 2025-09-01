from fastapi import APIRouter
from app.core.feature_flags import FeatureFlags

router = APIRouter()

@router.get("")
async def get_feature_flags():
    f = FeatureFlags()
    return {
        "enableGeoCheckin": f.ENABLE_GEO_CHECKIN,
        "enableSelfieCheckin": f.ENABLE_SELFIE_CHECKIN,
        "enableAiInsights": f.ENABLE_AI_INSIGHTS,
        "enablePhotoReminders": f.ENABLE_PHOTO_REMINDERS,
        "timezone": f.TIMEZONE,
    }
