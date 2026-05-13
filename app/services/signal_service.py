from app.clients.coingecko_client import CoinGeckoClient
from app.core.exceptions import NotEnoughMarketDataError
from app.indicators.momentum import calculate_rsi
from app.indicators.trend import sma
from app.schemas.signal import SignalResponse
from app.data.reasoning_texts import REASONING_TEXTS


class SignalService:
    def __init__(self) -> None:
        self.client = CoinGeckoClient()

    @staticmethod
    def _clamp(value: float, min_value: float, max_value: float) -> float:
        return max(min_value, min(value, max_value))

    def _build_reasoning(self, coin_id: str, action: str) -> str:
        coin_reasoning = REASONING_TEXTS.get(coin_id)

        if action in ("BUY", "STRONG_BUY"):
            sentiment = "bullish"
        elif action in ("SELL", "STRONG_SELL"):
            sentiment = "bearish"
        else:
            sentiment = "neutral"

        if coin_reasoning and sentiment in coin_reasoning:
            return coin_reasoning[sentiment]

        if sentiment == "bullish":
            return "AI detected bullish conditions with improving momentum and supportive market structure."

        if sentiment == "bearish":
            return "AI detected bearish conditions with weakening momentum and downside pressure."

        return "AI detected mixed market conditions with no strong directional confirmation."

    def generate_signal(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        ohlc_days: int = 7,
        timeframe: str = "4H",
    ) -> SignalResponse:
        market = self.client.get_coin_market_data(coin_id=coin_id, vs_currency=vs_currency)
        candles = self.client.get_ohlc(coin_id=coin_id, vs_currency=vs_currency, days=ohlc_days)

        if len(candles) < 20:
            raise NotEnoughMarketDataError("Not enough OHLC data to build signal")

        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]

        current_price = float(market["current_price"])
        sma20 = sma(closes, 20)
        rsi14 = calculate_rsi(closes, 14)
        momentum_24h = market.get("price_change_percentage_24h")

        recent_high = max(highs[-10:-1]) if len(highs) >= 10 else max(highs[:-1])
        recent_low = min(lows[-10:-1]) if len(lows) >= 10 else min(lows[:-1])

        breakout_up = current_price > recent_high
        breakout_down = current_price < recent_low

        bullish_score = 0
        bearish_score = 0

        if sma20 is not None:
            if current_price > sma20:
                bullish_score += 1
            else:
                bearish_score += 1

        if rsi14 is not None:
            if 50 <= rsi14 <= 68:
                bullish_score += 1
            elif rsi14 < 35:
                bullish_score += 1
            elif rsi14 > 72:
                bearish_score += 1
            elif rsi14 < 45:
                bearish_score += 1

        if momentum_24h is not None:
            if momentum_24h > 0:
                bullish_score += 1
            elif momentum_24h < 0:
                bearish_score += 1

        if breakout_up:
            bullish_score += 2
        if breakout_down:
            bearish_score += 2

        if bullish_score - bearish_score >= 2:
            action = "STRONG_BUY"
        elif bullish_score > bearish_score:
            action = "BUY"
        elif bearish_score - bullish_score >= 2:
            action = "STRONG_SELL"
        elif bearish_score > bullish_score:
            action = "SELL"
        else:
            action = "NEUTRAL"

        confidence = 50 + abs(bullish_score - bearish_score) * 10
        if breakout_up or breakout_down:
            confidence += 8
        if rsi14 is not None and (rsi14 < 35 or rsi14 > 65):
            confidence += 4
        confidence = int(self._clamp(confidence, 50, 95))

        ranges = [(h - l) for h, l in zip(highs[-14:], lows[-14:])]
        avg_range = sum(ranges) / len(ranges) if ranges else current_price * 0.02

        entry_price = current_price

        if action in ("BUY", "STRONG_BUY"):
            stop_loss = current_price - (avg_range * 1.2)
            target_1 = current_price + (avg_range * 1.5)
            target_2 = current_price + (avg_range * 2.4)
        elif action in ("SELL", "STRONG_SELL"):
            stop_loss = current_price + (avg_range * 1.2)
            target_1 = current_price - (avg_range * 1.5)
            target_2 = current_price - (avg_range * 2.4)
        else:
            stop_loss = current_price - avg_range
            target_1 = current_price + avg_range
            target_2 = current_price + (avg_range * 1.8)

        reasoning = self._build_reasoning(coin_id=coin_id, action=action)

        risk = abs(entry_price - stop_loss)
        reward = abs(target_2 - entry_price)
        risk_reward = round(reward / risk, 2) if risk > 0 else 0.0

        return SignalResponse(
            coin_id=market["id"],
            symbol=str(market["symbol"]).upper(),
            name=market["name"],
            current_price=round(current_price, 8),
            entry_price=round(entry_price, 8),
            target_1=round(target_1, 8),
            target_2=round(target_2, 8),
            stop_loss=round(stop_loss, 8),
            risk_reward=risk_reward,
            confidence=confidence,
            action=action,
            timeframe=timeframe,
            reasoning=reasoning,
            market_cap_rank=market.get("market_cap_rank"),
            price_change_percentage_24h=market.get("price_change_percentage_24h"),
            volume_24h=market.get("total_volume"),
        )