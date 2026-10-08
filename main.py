import telebot
import requests
import threading
import time
from flask import Flask

BOT_TOKEN = "8529280835:AAGMLiYBZpQ18H2XObFkC9Rmblih9A9CcqQ"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Gold Scalp Robot is Live!"
def get_coingecko_data():
    try:
        # 1st Try: Binance - sabse fast
        try:
            price_url = "https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT"
            price_data = requests.get(price_url, timeout=10).json()
            price = float(price_data['price'])

            # Chart ke liye Binance klines
            chart_url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=1h&limit=168"
            chart = requests.get(chart_url, timeout=15).json()
            prices = [float(c[4]) for c in chart]
        except:
            # 2nd Try: CoinGecko Backup
            price_url = "https://api.coingecko.com/api/v3/simple/price?ids=pax-gold&vs_currencies=usd"
            price_data = requests.get(price_url, timeout=15).json()
            price = float(price_data['pax-gold']['usd'])
            chart_url = "https://api.coingecko.com/api/v3/coins/pax-gold/market_chart?vs_currency=usd&days=7"
            chart = requests.get(chart_url, timeout=15).json()
            prices = [p[1] for p in chart['prices']]

        low_7d = min(prices)
        high_7d = max(prices)
        last_prices = prices[-100:] if len(prices) > 100 else prices

        def calc_rsi(prices_list, period=14):
            if len(prices_list) < period+1:
                return 50.0
            gains = []
            losses = []
            for i in range(1, len(prices_list)):
                diff = prices_list[i] - prices_list[i-1]
                if diff > 0:
                    gains.append(diff)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(diff))
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            if avg_loss == 0:
                return 70.0
            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))

        rsi = calc_rsi(last_prices)
        return price, low_7d, high_7d, rsi, last_prices

    except Exception as e:
        print(f"Price fetch error: {e}")
        return None
