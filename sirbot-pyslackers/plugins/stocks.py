import dataclasses
import os
from datetime import datetime
from decimal import Decimal


@dataclasses.dataclass(frozen=True)
class StockQuote:
    symbol: str
    company: str
    price: Decimal
    change: Decimal
    change_percent: Decimal
    market_open: Decimal
    market_close: Decimal
    high: Decimal
    low: Decimal
    volume: Decimal
    time: datetime


class StocksPlugin:
    __name__ = "stocks"

    def __init__(self):
        self.session = None  # set lazily on plugin load

    def load(self, sirbot):
        self.session = sirbot.http_session

    async def price(self, symbol: str) -> StockQuote:
        async with self.session.get(
            "https://query1.finance.yahoo.com/v7/finance/quote",
            params={
                "symbols": symbol,
            }
        ) as r:
            r.raise_for_status()
            body = (await r.json())["quoteResponse"]["result"]
            if len(body) < 1:
                return None

            quote = body[0]
            return StockQuote(
                symbol=quote["symbol"],
                company=quote["longName"],
                price=Decimal.from_float(quote["regularMarketPrice"]),
                change=Decimal.from_float(quote["regularMarketChange"]),
                change_percent=Decimal.from_float(quote["regularMarketChangePercent"]),
                market_open=Decimal.from_float(quote["regularMarketOpen"]),
                market_close=Decimal.from_float(quote["regularMarketPreviousClose"]),
                high=Decimal.from_float(quote["regularMarketDayHigh"]),
                low=Decimal.from_float(quote["regularMarketDayLow"]),
                volume=Decimal.from_float(quote["regularMarketVolume"]),
                time=datetime.fromtimestamp(quote["regularMarketTime"]),
            )

    async def crypto(self):
        """https://iextrading.com/developer/docs/#crypto"""
        url = self.API_ROOT + "/stock/market/crypto"
        async with self.session.get(url) as r:
            r.raise_for_status()
            return await r.json()
