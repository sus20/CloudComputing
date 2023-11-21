from pydantic import BaseModel,HttpUrl
from typing import Optional
from datetime import datetime

class CollectorFrame(BaseModel):
    timestamp: datetime
    image: str
    section: int
    event: str
    destination: Optional[HttpUrl] = None
    extra_info: Optional[str] = ""