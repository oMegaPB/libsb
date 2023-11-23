import asyncio
import typing as t
from pathlib import Path

from curl_cffi.requests import AsyncSession

TIMEOUT = 30

class ClientBase:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base = "https://api.hypixel.net/v2"
        self._uuid_cache: t.Dict[str, str] = {}
        self._session = None
        
    @property
    def session(self) -> AsyncSession:
        if self._session is None: 
            self._session = AsyncSession(impersonate="chrome110")
        self._session.headers.update({
            "Content-Type": "application/json",
            "API-Key": self.api_key,
            "User-Agent": "Mozilla/5.0 sbClient v1.0",
        })
        return self._session

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        return False