
---

# Roboback

Roboback é um projeto desenvolvido em Django com Python 3, focado na criação de um robô de trading automatizado para o mercado Forex. O sistema utiliza diversas técnicas avançadas de aprendizado e automação para tomar decisões de compra e venda, com base em indicadores financeiros personalizados.

## Estrutura do Projeto

A estrutura do projeto é organizada da seguinte forma:

```
roboback/
│
├── robotrader/
│   ├── automacao/
│   │   ├── __pycache__/
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── __pycache__/
│   ├── __init__.py
│   ├── asgi.py
│   ├── logging_config.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── services/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── api_service.py
│   ├── chart_data_service.py
│   ├── constants.py
│   ├── currency_pair_service.py
│   ├── decision_service.py
│   ├── indicator_service.py
│   ├── learning_service.py
│   ├── robo_service.py
│   └── util_service.py
│
└── node_modules/
```

## Requisitos

- Python 3
- Django
- Ambiente virtual (virtualenv)

## Configuração do Ambiente de Desenvolvimento

### Passo 1: Clonar o Repositório

Clone o repositório para a sua máquina local:

```sh
git clone <URL_DO_REPOSITORIO>
cd roboback
```

### Passo 2: Ativar o Ambiente Virtual

Ative o ambiente virtual existente:

- No Linux/MacOS:

  ```sh
  source venv/bin/activate
  ```

- No Windows:

  ```sh
  venv\Scripts\activate
  ```

### Passo 3: Instalar Dependências

Com o ambiente virtual ativado, instale as dependências do projeto:

```sh
pip3 install -r requirements.txt
```

### Passo 4: Aplicar as Migrações do Banco de Dados

Aplique as migrações para configurar o banco de dados:

```sh
cd robotrader
python3 manage.py migrate
```

### Passo 5: Iniciar o Servidor de Desenvolvimento

Entre na pasta `robotrader` e inicie o servidor de desenvolvimento do Django:

```sh
cd robotrader
python3 manage.py runserver
```

## Descrição dos Serviços

### RoboService

- **Função:** `RoboService` é o serviço principal que gerencia todo o processo de monitoramento, análise e tomada de decisões de trading. Ele é o "cérebro" do sistema, coordenando a execução de tarefas e interagindo com os outros serviços.
- **Responsabilidades:**
  - **Monitoramento Contínuo:** Executa um loop contínuo (`run_observer`) que verifica periodicamente os pares de moedas disponíveis e aciona a lógica de análise e decisão.
  - **Processamento de Pares:** Para cada par de moedas, coleta dados históricos e em tempo real, e decide se deve comprar, vender ou manter a posição.
  - **Atualização de Decisões:** Se a nova decisão for diferente da anterior, ele atualiza o sistema com a nova decisão e armazena os resultados.

### ChartDataService

- **Função:** Responsável por coletar e fornecer dados de mercado, incluindo preços históricos e em tempo real.
- **Responsabilidades:**
  - **Coleta de Dados:** Usa APIs e websockets para coletar dados de mercado para pares de moedas.
  - **Cache de Dados:** Implementa caching para melhorar a eficiência e reduzir o número de chamadas às APIs externas.
  - **Visualização de Dados:** Oferece métodos para plotar gráficos de candlestick dos dados coletados.

### CurrencyPairService

- **Função:** Atua como um intermediário entre o `ChartDataService` e o `DecisionService`, gerenciando os pares de moedas e fornecendo os dados necessários para a tomada de decisões.
- **Responsabilidades:**
  - **Gerenciamento de Pares de Moedas:** Obtém e gerencia a lista de pares de moedas disponíveis.
  - **Fornecimento de Dados:** Reúne os dados necessários (coletados pelo `ChartDataService`) e os fornece ao `DecisionService` para análise.

### DecisionService

- **Função:** Realiza a análise dos dados de mercado para tomar decisões de compra, venda ou manutenção de posições em pares de moedas.
- **Responsabilidades:**
  - **Tomada de Decisões:** Analisa os dados fornecidos pelo `CurrencyPairService`, utilizando indicadores técnicos, para determinar a melhor ação a ser tomada.
  - **Integração com Outros Serviços:** Colabora com outros serviços, como o `LearningService`, para melhorar as decisões ao longo do tempo.
  - **Sistema de Pesos e Pontuação:** Implementa um sistema de pontuação e pesos que é ajustado continuamente com base nos resultados das decisões passadas. Este sistema utiliza uma combinação de memória de curto e longo prazo, janelas deslizantes, e decaimento exponencial para garantir que o robô de trading se adapte às condições de mercado de forma eficaz.

### IndicatorService

- **Função:** Responsável exclusivamente pelo cálculo dos indicadores técnicos utilizados nas análises.
- **Responsabilidades:**
  - **Cálculo de Indicadores:** Fornece métodos para calcular indicadores como SMA, EMA, RSI, Bandas de Bollinger, ADX, e outros. Esses cálculos são isolados para garantir que o `DecisionService` possa se concentrar na lógica de decisão.

### UtilService

- **Função:** Fornece funcionalidades utilitárias e auxiliares, como validação de dados e operações genéricas que suportam o fluxo de trabalho de outros serviços.
- **Responsabilidades:**
  - **Validação de Séries Temporais:** Realiza validações nas séries de preços para garantir que os dados estão no formato esperado e são suficientes para o cálculo dos indicadores.
  - **Operações Genéricas:** Oferece métodos utilitários que suportam operações comuns entre diferentes partes do sistema, como normalização de pesos e cálculo de mudanças de preços.

### LearningService

- **Função:** Aprimora o modelo de decisão ao longo do tempo, ajustando os pesos dos indicadores técnicos com base nos resultados das decisões anteriores.
- **Responsabilidades:**
  - **Ajuste de Pesos:** Modifica os pesos dos indicadores técnicos com base no sucesso ou falha das decisões de trading, utilizando uma combinação de memória de curto e longo prazo, janelas deslizantes, e decaimento exponencial.
  - **Normalização e Armazenamento:** Garante que os pesos estejam balanceados e armazena-os no banco de dados para uso futuro.
  - **Taxa de Aprendizado:** Gerencia a taxa de aprendizado, permitindo que o modelo se ajuste de forma gradual e controlada.
  - **Memória de Curto e Longo Prazo:** Mantém uma memória de curto prazo (através de janelas deslizantes) e uma memória de longo prazo (com ajuste gradual) para garantir que o sistema se adapte tanto às condições imediatas quanto às tendências de mercado mais duradouras.

## Serviços e Funcionalidades

### Automacao

O módulo `automacao` é responsável por gerenciar os processos de sinalização de compra e venda em daytrade. Ele inclui:

- `admin.py`: Configurações do Django Admin para o app.
- `apps.py`: Configurações do app `automacao`.
- `models.py`: Definição dos modelos de dados.
- `tests.py`: Testes automatizados.
- `urls.py`: Configurações de URL para o app `automacao`.
- `views.py`: Definição das views para o app `automacao`.

### Services

O diretório `services` contém serviços auxiliares para o projeto, como:

- `api_service.py`: Serviço responsável por integrar o sistema com APIs externas necessárias para o funcionamento do robô de trading.
- `chart_data_service.py`: Serviço responsável por coletar e fornecer dados de mercado.
- `constants.py`: Arquivo que contém constantes usadas no sistema.
- `currency_pair_service.py`: Serviço que gerencia os pares de moedas e interage com o `ChartDataService` e `DecisionService`.
- `decision_service.py`: Serviço que realiza a análise dos dados de mercado para tomar decisões de trading.
- `indicator_service.py`: Serviço especializado no cálculo de indicadores técnicos.
- `learning_service.py`: Serviço que ajusta e aprimora os pesos dos indicadores técnicos com base no desempenho passado.
- `robo_service.py`: Serviço principal que orquestra todos os outros serviços para realizar o trading automatizado.
- `util_service.py`: Serviço de utilitários que fornece validações e operações auxiliares para suportar os demais serviços.

## Autor

- **Rafael Dias**
  - [GitHub](https://github.com/rafasdiass)
  - [LinkedIn

](https://www.linkedin.com/in/rdrafaeldias/)
  - Email: rafasdiasdev@gmail.com

--- 

