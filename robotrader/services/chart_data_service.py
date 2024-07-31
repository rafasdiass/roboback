import logging
import requests
import pandas as pd
import asyncio
import websockets
import json
import time
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ChartDataService:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3/klines"
        self.websocket_url = "wss://stream.binance.com:9443/ws"
        self.cache = {}
        self.cache_duration = 60 * 60  # Cache por 1 hora

    async def get_realtime_data(self, symbol):
        """Obtém dados de preço em tempo real para um par de moedas específico."""
        try:
            ws_url = f"{self.websocket_url}/{symbol.lower()}@kline_1m"
            async with websockets.connect(ws_url) as websocket:
                async for message in websocket:
                    data = json.loads(message)
                    kline = data['k']
                    yield {
                        'Open Time': datetime.fromtimestamp(kline['t'] / 1000),
                        'Open': float(kline['o']),
                        'High': float(kline['h']),
                        'Low': float(kline['l']),
                        'Close': float(kline['c']),
                        'Volume': float(kline['v']),
                        'Close Time': datetime.fromtimestamp(kline['T'] / 1000),
                        'Quote Asset Volume': float(kline['q']),
                        'Number of Trades': int(kline['n']),
                        'Taker Buy Base Asset Volume': float(kline['V']),
                        'Taker Buy Quote Asset Volume': float(kline['Q'])
                    }
        except Exception as e:
            logging.error(f"Erro ao obter dados em tempo real para {symbol}: {e}")
            raise

    async def fetch_intraday_data(self, symbol, interval='1m', limit=100):
        """Obtém dados de preços intraday para um par de moedas em um intervalo específico."""
        cache_key = f"{symbol}_{interval}"
        current_time = time.time()
        
        # Verifica se os dados estão no cache e ainda são válidos
        if cache_key in self.cache and (current_time - self.cache[cache_key]['timestamp'] < self.cache_duration):
            logging.info(f"Dados de cache usados para {symbol} no intervalo {interval}")
            return self.cache[cache_key]['data'], 'cache'
        
        try:
            params = {'symbol': symbol, 'interval': interval, 'limit': limit}
            response = requests.get(self.base_url, params=params)
            data = response.json()

            if not data or 'code' in data:
                raise ValueError(f"Erro ao buscar dados históricos para {symbol} com intervalo {interval}")

            df = pd.DataFrame(data, columns=[
                'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
                'Close Time', 'Quote Asset Volume', 'Number of Trades',
                'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'
            ])
            df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
            df.set_index('Open Time', inplace=True)
            
            # Armazena no cache
            self.cache[cache_key] = {'data': df, 'timestamp': current_time}
            return df, 'real'
        except Exception as e:
            logging.error(f"Erro ao buscar dados históricos para {symbol} com intervalo {interval}: {e}")
            raise

    def get_available_symbols(self):
        """Obtém a lista de símbolos disponíveis."""
        try:
            response = requests.get("https://api.binance.com/api/v3/exchangeInfo")
            data = response.json()
            symbols = [symbol['symbol'] for symbol in data['symbols']]
            return symbols
        except Exception as e:
            logging.error(f"Erro ao buscar lista de símbolos disponíveis: {e}")
            return []

    def plot_candlestick(self, df, symbol):
        """Gera um gráfico de candlestick usando plotly."""
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True)

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name=symbol
        ))

        fig.update_layout(title=f'Candlestick Chart for {symbol}',
                          xaxis_title='Time',
                          yaxis_title='Price')

        fig.show()
