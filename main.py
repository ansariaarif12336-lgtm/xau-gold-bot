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
        # Try Binance First
        price_url = "https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT"
        r = requests.get(price_url, timeout=10)
        price = float(r.json()['price'])

        chart_url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=1h&limit=168"
        chart_data = requests.get(chart_url, timeout=15).json()
        prices = [float(c[4]) for c in chart_data]

        low_7d = min(prices)
        high_7d = max(prices)
        last_prices = prices[-100:] if len(prices) > 100 else prices

        # RSI Calc
        def calc_rsi(lst, period=14):
            if len(lst) < period+1: return 50.0
            gains = 0
            losses = 0
            for i in range(1, period+1):
                diff = lst[-i] - lst[-i-1]
                if diff > 0: gains += diff
                else: losses += abs(diff)
            if losses == 0: return 70.0
            rs = (gains/period) / (losses/period)
            return 100 - (100/(1+rs))

        rsi = calc_rsi(last_prices)
        return price, low_7d, high_7d, rsi, last_prices
    except Exception as e:
        print(f"Fetch Error: {e}")
        return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "Gold Scalp Robot Live!\n\n/paxg - Gold Price + Signal\n/xau - Same as PAXG\n/xag - Silver Price")

@bot.message_handler(commands=['paxg','xau','gold'])
def paxg(m):
    data = get_coingecko_data()
    if not data:
        bot.reply_to(m, "Price fetch failed. Try again after 1 min.")
        return
    price, low, high, rsi, _ = data
    signal = "BUY" if rsi < 35 else "SELL" if rsi > 70 else "HOLD"
    msg = f"🪙 PAXG Gold: ${price:.2f}\n7D Low: ${low:.2f} | High: ${high:.2f}\nRSI: {rsi:.1f}\nSignal: {signal}"
    bot.reply_to(m, msg)

@bot.message_handler(commands=['xag','silver'])
def xag(m):
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=XAGUSDT"
        # Binance pe XAG nahi hai to fallback
        raise Exception("fallback")
    except:
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=tethered-silver&vs_currencies=usd"
            r = requests.get(url, timeout=10).json()
            price = r['tethered-silver']['usd']
            bot.reply_to(m, f"🥈 Silver (XAG): ${price}")
        except:
            bot.reply_to(m, "Silver price fetch failed.")

def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(5)

threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
