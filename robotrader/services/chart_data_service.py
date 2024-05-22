import logging
import pandas as pd
from dotenv import load_dotenv
import os
import httpx
import asyncio
import time
import numpy as np

load_dotenv()
api_key = os.getenv("EODHD_API_KEY", "demo")  # Usando chave de API demo como padrão

class ChartDataService:
    def __init__(self, api_key=api_key):
        self.api_key = api_key
        self.cache = {}
        self.cache_duration = 60 * 60  # Cache por 1 hora

    async def fetch_intraday_data(self, symbol, interval='1m', outputsize='compact'):
        cache_key = f"{symbol}_{interval}"
        current_time = time.time()
        
        # Verifica se os dados estão no cache e ainda são válidos
        if cache_key in self.cache and (current_time - self.cache[cache_key]['timestamp'] < self.cache_duration):
            logging.info(f"Dados de cache usados para {symbol} no intervalo {interval}")
            return self.cache[cache_key]['data'], 'cache'
        
        # Ajuste a URL para usar a chave de API demo
        url = f"https://eodhd.com/api/intraday/{symbol}?interval={interval}&api_token={self.api_key}&fmt=json"
        logging.info(f"Buscando dados para {symbol} com URL: {url}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code != 200:
                    raise httpx.HTTPStatusError(f"Erro HTTP {response.status_code} para URL {url}", request=response.request, response=response)
                data = response.json()
                if "data" in data:
                    formatted_data = self._format_data(data["data"])
                    # Armazena no cache
                    self.cache[cache_key] = {'data': formatted_data, 'timestamp': current_time}
                    return formatted_data, 'real'
                elif "error" in data:
                    raise Exception(data["error"])
                else:
                    logging.error(f"Erro ao buscar dados para {symbol}: {data}")
                    raise Exception(f"Erro ao buscar dados para {symbol}")
        except httpx.HTTPStatusError as e:
            logging.error(f"Erro HTTP ao buscar dados para {symbol}: {e}")
            logging.error(f"URL: {url}")
            logging.error(f"API Key: {self.api_key}")
            raise
        except httpx.RequestError as e:
            logging.error(f"Erro de requisição ao buscar dados para {symbol}: {e}")
            raise
        except ValueError as e:
            logging.error(f"Erro ao processar a resposta da API para {symbol}: {e}. Resposta: {response.text}")
            raise
        except Exception as e:
            logging.error(f"Erro ao buscar dados para {symbol}: {e}")
            # Gera dados simulados se o limite de solicitações for atingido
            simulated_data = self._generate_simulated_data(symbol, interval)
            return simulated_data, 'simulated'

    @staticmethod
    def _format_data(data):
        df = pd.DataFrame(data)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        return df
    
    @staticmethod
    def _generate_simulated_data(symbol, interval):
        logging.warning(f"Gerando dados simulados para {symbol} no intervalo {interval}")
        date_range = pd.date_range(end=pd.Timestamp.now(), periods=100, freq=interval)
        data = {
            'open': np.random.random(size=100) * 100,
            'high': np.random.random(size=100) * 100,
            'low': np.random.random(size=100) * 100,
            'close': np.random.random(size=100) * 100,
            'volume': np.random.randint(1, 100, size=100)
        }
        df = pd.DataFrame(data, index=date_range)
        return df

# Ajuste para uso no Django
def fetch_intraday_data_sync(symbol, interval='1m', outputsize='compact'):
    service = ChartDataService()
    data, source = asyncio.run(service.fetch_intraday_data(symbol, interval, outputsize))
    return data, source
