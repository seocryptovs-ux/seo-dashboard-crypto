from fastapi import Header, HTTPException

from app.core.config import settings


def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="x-api-key header is missing")

    if not settings.API_KEY:
        raise HTTPException(status_code=500, detail="API key is not configured on server")

    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")