from fastapi import FastAPI, Query
import httpx
import time

app = FastAPI(title="nassrapi", version="1.0")

BASE_URLS = [
    "https://api3.binance.com",
    "https://api1.binance.com",
    "https://api4.binance.com",
    "https://api.binance.com",
]

CACHE = {}
CACHE_TTL = 2


async def fetch_symbol(client, base, symbol):
    try:
        url = f"{base}/api/v3/ticker/24hr?symbol={symbol}"
        r = await client.get(url, timeout=5)

        if r.status_code == 200:
            data = r.json()

            return {
                "symbol": data.get("symbol"),
                "price": data.get("lastPrice"),
                "volume": data.get("volume"),
                "change": data.get("priceChangePercent")
            }
    except:
        return None


async def get_price(symbol: str):
    async with httpx.AsyncClient() as client:
        for base in BASE_URLS:
            result = await fetch_symbol(client, base, symbol)
            if result:
                return result
    return None


@app.get("/api/price")
async def price(symbol: str = Query(default="XRPUSDT")):
    symbol = symbol.upper()
    now = time.time()

    if symbol in CACHE:
        cached_data, timestamp = CACHE[symbol]

        if now - timestamp < CACHE_TTL:
            return {
                "api": "nassrapi",
                "status": "success",
                "cached": True,
                "data": cached_data
            }

    data = await get_price(symbol)

    if data:
        CACHE[symbol] = (data, now)

        return {
            "api": "nassrapi",
            "status": "success",
            "cached": False,
            "data": data
        }

    return {
        "api": "nassrapi",
        "status": "error",
        "message": "All Binance endpoints failed"
    }
