from typing import Any, Dict, List, Optional

import requests

from app.core.config import settings
from app.core.exceptions import CoinGeckoRequestError, CoinNotFoundError


class CoinGeckoClient:
    def __init__(self) -> None:
        self.timeout = settings.COINGECKO_TIMEOUT
        self.session = requests.Session()

        if settings.COINGECKO_PLAN == "pro":
            self.base_url = "https://pro-api.coingecko.com/api/v3"
            if settings.COINGECKO_API_KEY:
                self.session.headers.update({
                    "x-cg-pro-api-key": settings.COINGECKO_API_KEY
                })
        else:
            self.base_url = "https://api.coingecko.com/api/v3"
            if settings.COINGECKO_API_KEY:
                self.session.headers.update({
                    "x-cg-demo-api-key": settings.COINGECKO_API_KEY
                })

        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "crypto-signals-backend/1.0"
        })

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{path}"
        response = self.session.get(url, params=params, timeout=self.timeout)

        if response.status_code == 429:
            raise CoinGeckoRequestError("Rate limit exceeded in CoinGecko")

        if not response.ok:
            raise CoinGeckoRequestError(
                f"CoinGecko error {response.status_code}: {response.text}"
            )

        return response.json()

    def get_coin_market_data(self, coin_id: str, vs_currency: str = "usd") -> Dict[str, Any]:
        data = self._get(
            "/coins/markets",
            params={
                "vs_currency": vs_currency,
                "ids": coin_id,
                "price_change_percentage": "24h,7d",
            },
        )

        if not data:
            raise CoinNotFoundError(f"Coin '{coin_id}' not found")

        return data[0]

    def get_ohlc(self, coin_id: str, vs_currency: str = "usd", days: int = 7) -> List[Dict[str, float]]:
        raw = self._get(
            f"/coins/{coin_id}/ohlc",
            params={
                "vs_currency": vs_currency,
                "days": days,
            },
        )

        candles: List[Dict[str, float]] = []
        for item in raw:
            candles.append({
                "timestamp": float(item[0]),
                "open": float(item[1]),
                "high": float(item[2]),
                "low": float(item[3]),
                "close": float(item[4]),
            })

        return candles