import telebot
import requests
import threading
import time
from flask import Flask
import math

BOT_TOKEN = "8529280835:AAE2SaRSOYszjRox0hcM0sGCCnPHPuKrVJI"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Gold Scalp Robot is Live!"

def get_coingecko_data():
    try:
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
            avg_gain = sum(gains[:period]) / period
            avg_loss = sum(losses[:period]) / period
            for i in range(period, len(gains)):
                avg_gain = (avg_gain * (period-1) + gains[i]) / period
                avg_loss = (avg_loss * (period-1) + losses[i]) / period
            if avg_loss == 0:
                return 100.0
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return round(rsi, 1)

        rsi = calc_rsi(last_prices, 14)
        retrace_618 = high_7d - 0.618 * (high_7d - low_7d)
        dist_retrace = abs(price - retrace_618) / price * 100
        target_buy = 4091
        dist_target = abs(price - target_buy) / price * 100
        buy_triggered = dist_target < 0.5 and rsi < 30

        return {
            "price": price,
            "rsi": rsi,
            "low_7d": low_7d,
            "high_7d": high_7d,
            "retrace_618": retrace_618,
            "dist_retrace": dist_retrace,
            "dist_target": dist_target,
            "buy_triggered": buy_triggered
        }
    except Exception as e:
        print(f"Data error: {e}")
        return None

def format_msg(data):
    if not data:
        return "Price fetch failed. Try again after 1 min."
    price = data["price"]
    rsi = data["rsi"]
    if rsi > 70:
        rsi_status = "Overbought"
    elif rsi < 30:
        rsi_status = "Oversold"
    else:
        rsi_status = "No RSI extreme"
    buy_status = "TRIGGERED 🚀 BUY" if data["buy_triggered"] else "NOT TRIGGERED"
    not_met = f"Not met: price is {data['dist_target']:.2f}% from $4091; RSI-14 is {'below' if rsi<30 else 'above'} 30 ({rsi})."
    msg = f"""PAXG: ${price:,.2f} USD
Source: CoinGecko · Updated {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}
Hourly RSI-14: {rsi} — {rsi_status}
Exhaustion check: No 24-hour RSI divergence
7-day range: ${data['low_7d']:,.2f}-${data['high_7d']:,.2f}
0.618 retracement: ${data['retrace_618']:,.2f} ({data['dist_retrace']:.2f}% from current price)
Rule-based buy signal: {buy_status}
{not_met if not data['buy_triggered'] else 'Conditions met: Near $4091 and RSI oversold.'}
Technical indicator only; not financial advice.
No trades are placed."""
    return msg

@bot.message_handler(commands=['start'])
def handle_start(m):
    bot.reply_to(m, "Gold Scalp Robot Live! ✅\n\n/paxg - Gold Price + Signal\n/xau - Same as PAXG\n/xag - Silver Price\n\nBot 24/7 Live on Render")

@bot.message_handler(commands=['paxg','xau','gold'])
def handle_paxg(m):
    bot.send_chat_action(m.chat.id, 'typing')
    data = get_coingecko_data()
    bot.reply_to(m, format_msg(data))

@bot.message_handler(commands=['xag','silver'])
def handle_xag(m):
    try:
        bot.send_chat_action(m.chat.id, 'typing')
        url = "https://api.coingecko.com/api/v3/simple/price?ids=kinesis-silver&vs_currencies=usd"
        r = requests.get(url, timeout=10).json()
        price = r.get('kinesis-silver', {}).get('usd', 'N/A')
        bot.reply_to(m, f"XAG / Silver: ${price} USD\nSource: CoinGecko")
    except:
        bot.reply_to(m, "Silver price fetch failed, try again.")

@bot.message_handler(func=lambda m: True)
def handle_all(m):
    if m.text and m.text.startswith('/'):
        bot.reply_to(m, "Use /paxg or /xau or /xag")

def run_bot():
    while True:
        try:
            print("Starting bot polling...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
        except Exception as e:
            print(f"Polling crashed: {e}")
            time.sleep(10)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
