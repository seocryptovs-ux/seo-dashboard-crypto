from fastapi import APIRouter, Depends, HTTPException

from app.core.exceptions import (
    CoinGeckoRequestError,
    CoinNotFoundError,
    NotEnoughMarketDataError,
)
from app.dependencies.auth import verify_api_key
from app.schemas.signal import SignalResponse
from app.services.signal_service import SignalService

router = APIRouter(prefix="/signals", tags=["signals"])
service = SignalService()


@router.get("/{coin_id}", response_model=SignalResponse)
def get_signal(
    coin_id: str,
    vs_currency: str = "usd",
    ohlc_days: int = 7,
    timeframe: str = "4H",
    _: None = Depends(verify_api_key),
):
    try:
        return service.generate_signal(
            coin_id=coin_id,
            vs_currency=vs_currency,
            ohlc_days=ohlc_days,
            timeframe=timeframe,
        )
    except CoinNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotEnoughMarketDataError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except CoinGeckoRequestError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/test/buy")
def test_buy():
    return {
        "coin_id": "testcoin",
        "symbol": "TEST",
        "name": "Test Coin",
        "current_price": 100,
        "entry_price": 100,
        "target_1": 108,
        "target_2": 115,
        "stop_loss": 96,
        "risk_reward": 3.75,
        "confidence": 88,
        "action": "STRONG_BUY",
        "timeframe": "4H",
        "reasoning": "Test bullish signal."
    }