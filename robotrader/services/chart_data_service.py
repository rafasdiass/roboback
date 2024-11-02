import zmq
import logging
import pandas as pd
import numpy as np
from datetime import datetime

logging.basicConfig(level=logging.INFO)

class ChartDataService:
    def __init__(self, zmq_address="tcp://127.0.0.1:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(zmq_address)
        logging.info(f"Servidor ZeroMQ iniciado e escutando em {zmq_address}")

    def _generate_signal(self, data):
        try:
            df = pd.DataFrame(data)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df.set_index('datetime', inplace=True)

            df['SMA_5'] = df['close'].rolling(window=5).mean()
            df['SMA_20'] = df['close'].rolling(window=20).mean()

            if df['SMA_5'].iloc[-1] > df['SMA_20'].iloc[-1]:
                return "COMPRA"
            elif df['SMA_5'].iloc[-1] < df['SMA_20'].iloc[-1]:
                return "VENDA"
            else:
                return "MANTER"
        except Exception as e:
            logging.error(f"Erro ao gerar sinal: {e}")
            return "ERRO"

    def run(self):
        while True:
            message = self.socket.recv_json()
            logging.info(f"Dados recebidos: {message}")

            signal = self._generate_signal(message['data'])
            response = {"sinal": signal, "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            self.socket.send_json(response)
            logging.info(f"Sinal enviado: {response}")

if __name__ == "__main__":
    service = ChartDataService()
    service.run()
