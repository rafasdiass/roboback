# services/eodhd_service.py
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

class EODHDService:
    def __init__(self):
        self.api_key = os.getenv("EODHD_API_KEY")
        self.base_url = 'https://eodhistoricaldata.com/api'

    async def get_historical_data(self, symbol, from_date, to_date, interval='5m'):
        url = f"{self.base_url}/eod/{symbol}"
        params = {
            'api_token': self.api_key,
            'from': from_date,
            'to': to_date,
            'interval': interval,
            'fmt': 'json'
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
