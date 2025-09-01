from pydantic import BaseModel
from typing import Optional, Dict

class PushSubscriptionIn(BaseModel):
    endpoint: str
    keys: Dict[str, str]  # {'p256dh': '...', 'auth':'...'}
    user_agent: Optional[str] = None

class PushPublicKeyOut(BaseModel):
    public_key: str  # base64url
