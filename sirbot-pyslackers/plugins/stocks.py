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


@dataclasses.dataclasses(frozen=True)
class CryptoQuote:
    symbol: str
    name: str
    price: Decimal
    link: str
    change_24hr_percent: Decimal


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

    async def crypto(self, symbol: str) -> CryptoQuote:
        """https://docs.coincap.io"""
        async with self.session.get("https://api.coincap.io/v2/rates/") as r:
            r.raise_for_status()
            top_assets = await r.json()

        symbol = symbol.lower()
        for asset in top_assets["data"]:
            if asset["symbol"].lower() == symbol:
                return CryptoQuote(
                    symbol=asset["symbol"],
                    name=asset["name"] or "",
                    price=Decimal(asset["priceUsd"]),
                    link="https://coincap.io/assets/" + asset["id"],
                    change_24hr_percent=Decimal(asset["changePercent24Hr"]),
                )
