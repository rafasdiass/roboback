# services/util_service.py

class UtilService:
    @staticmethod
    def calculate_rsi(prices, period=7):
        gains = 0
        losses = 0

        for i in range(1, period + 1):
            difference = prices[i] - prices[i - 1]
            if difference >= 0:
                gains += difference
            else:
                losses -= difference

        avg_gain = gains / period
        avg_loss = losses / period

        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs)) if avg_loss != 0 else 100

        return rsi

    @staticmethod
    def calculate_ema(prices, period=9):
        ema = prices[0]
        multiplier = 2 / (period + 1)

        for price in prices[1:]:
            ema = ((price - ema) * multiplier) + ema

        return ema

    @staticmethod
    def ema_9_period_rule(prices):
        ema9 = UtilService.calculate_ema(prices, 9)
        first_candle = prices[1]
        second_candle = prices[2]
        third_candle = prices[0]

        if first_candle < ema9 < third_candle and second_candle < ema9:
            return "Retrair"
        return "Sem sinal"

    @staticmethod
    def calculate_sma(prices, period):
        return sum(prices[:period]) / period

    @staticmethod
    def calculate_price_change(prices):
        initial_price = prices[-1]
        final_price = prices[0]
        return ((final_price - initial_price) / initial_price) * 100 if initial_price != 0 else 0

    @staticmethod
    def calculate_stochastic_oscillator(prices, period=14):
        recent_prices = prices[:period]
        lowest_price = min(recent_prices)
        highest_price = max(recent_prices)
        current_price = prices[0]

        if highest_price == lowest_price:
            return 100

        return ((current_price - lowest_price) / (highest_price - lowest_price)) * 100

    @staticmethod
    def calculate_fibonacci_levels(low, high):
        diff = high - low
        return {
            '0.0%': low,
            '23.6%': low + diff * 0.236,
            '38.2%': low + diff * 0.382,
            '50.0%': low + diff * 0.5,
            '61.8%': low + diff * 0.618,
            '100.0%': high
        }

    @staticmethod
    def identify_patterns(prices):
        w_patterns = []
        m_patterns = []

        for i in range(4, len(prices)):
            slice = prices[i - 4:i + 1]

            if slice[0] > slice[1] < slice[2] > slice[3] < slice[4]:
                w_patterns.append(i)

            if slice[0] < slice[1] > slice[2] < slice[3] > slice[4]:
                m_patterns.append(i)

        return {'wPatterns': w_patterns, 'mPatterns': m_patterns}

    @staticmethod
    def calculate_support_and_resistance(prices):
        low = min(prices)
        high = max(prices)
        close = prices[0]

        pivot_point = (low + high + close) / 3
        support = 2 * pivot_point - high
        resistance = 2 * pivot_point - low

        return {'support': support, 'resistance': resistance}

    @staticmethod
    def apply_retracement_strategy(prices, time_frame):
        levels = UtilService.calculate_support_and_resistance(prices)
        current_price = prices[0]

        if time_frame == '5min' and levels['support'] < current_price < levels['resistance']:
            return "Retrace"
        elif time_frame == '15min' and levels['support'] < current_price < levels['resistance']:
            return "Retrace"
        return "No Signal"

    @staticmethod
    def apply_composite_retracement_strategy(prices_5min, prices_15min):
        retracement_5min = UtilService.apply_retracement_strategy(prices_5min, '5min')
        retracement_15min = UtilService.apply_retracement_strategy(prices_15min, '15min')

        if retracement_5min == "Retrace" and retracement_15min == "Retrace":
            return "Strong Retrace"
        return "No Signal"
