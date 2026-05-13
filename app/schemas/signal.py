from typing import Literal, Optional

from pydantic import BaseModel


SignalAction = Literal["BUY", "SELL", "STRONG_BUY", "STRONG_SELL", "NEUTRAL"]


class SignalResponse(BaseModel):
    coin_id: str
    symbol: str
    name: str

    current_price: float
    entry_price: float
    target_1: float
    target_2: float
    stop_loss: float

    risk_reward: float
    confidence: int
    action: SignalAction
    timeframe: str
    reasoning: str

    market_cap_rank: Optional[int] = None
    price_change_percentage_24h: Optional[float] = None
    volume_24h: Optional[float] = None