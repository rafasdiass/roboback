from datetime import datetime
import requests
import pandas as pd


import requests
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Função para obter dados de candlestick do dia atual
def get_candlestick_data(symbol, interval):
    # Endpoint da Binance para obter dados de candlestick
    base_url = "https://api.binance.com/api/v3/klines"

    # Definindo o tempo de início e fim para o dia de hoje
    now = datetime.now()
    start_of_day = datetime(now.year, now.month, now.day)
    start_time = int(start_of_day.timestamp() * 1000)  # Converte para milissegundos

    # Fazendo a solicitação para o endpoint da Binance
    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': start_time
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    # Convertendo os dados para um DataFrame
    df = pd.DataFrame(data, columns=[
        'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Close Time', 'Quote Asset Volume', 'Number of Trades',
        'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'
    ])

    # Convertendo colunas numéricas para float
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)
    df['Volume'] = df['Volume'].astype(float)

    # Convertendo timestamps para datetime
    df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
    df['Close Time'] = pd.to_datetime(df['Close Time'], unit='ms')

    # Definindo 'Open Time' como índice
    df.set_index('Open Time', inplace=True)

    return df


# Main
def main():
    # Obtendo dados de candlestick do dia atual
    symbol = 'BTCUSDT'
    interval = '1m'  # Intervalo de 1 minuto

    df = get_candlestick_data(symbol, interval)

    print(df)

if __name__ == '__main__':
    main()



