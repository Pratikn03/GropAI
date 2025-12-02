import os

from fastapi import Depends, Header, HTTPException


def require_api_key(x_api_key: str | None = Header(default=None)):
    expected = os.getenv("API_KEY")
    if not expected:
        return True
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True
