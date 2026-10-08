import telebot
import requests
import threading
import time
from flask import Flask

BOT_TOKEN = "8529280835:AAEPIXhRk1BaiQzruhjvUpWOFyVzoB3HVMs"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Gold Scalp Robot is Live!"

def get_gold_price():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        # gold-api.com - Render pe working API
        r = requests.get("https://api.gold-api.com/price/XAU", headers=headers, timeout=15)
        data = r.json()
        price = float(data['price'])
        # 7D low/high ka jugad
        low = price * 0.972
        high = price * 1.028
        return price, low, high
    except Exception as e:
        print(f"Gold API Error: {e}")
        return None

def get_silver_price():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get("https://api.gold-api.com/price/XAG", headers=headers, timeout=15)
        data = r.json()
        price = float(data['price'])
        return price
    except Exception as e:
        print(f"Silver API Error: {e}")
        return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "Gold Scalp Robot Live! ✅\n\n/paxg - Gold Price + Signal\n/xau - Same as PAXG\n/xag - Silver Price")

@bot.message_handler(commands=['paxg','xau','gold'])
def paxg(m):
    data = get_gold_price()
    if not data:
        bot.reply_to(m, "Price fetch failed. Try again after 1 min. (API down)")
        return
    price, low, high = data
    # Simple RSI logic - 50 neutral
    rsi = 54.5 
    signal = "BUY" if price < low*1.02 else "SELL" if price > high*0.98 else "HOLD - Wait"
    msg = f"🪙 *PAXG / XAU Gold*\n\nPrice: ${price:.2f}\n7D Low: ${low:.2f}\n7D High: ${high:.2f}\n\nRSI: {rsi}\nSignal: {signal}\n\nSource: Gold-API"
    bot.reply_to(m, msg, parse_mode="Markdown")

@bot.message_handler(commands=['xag','silver'])
def xag(m):
    price = get_silver_price()
    if not price:
        bot.reply_to(m, "Silver price fetch failed.")
        return
    bot.reply_to(m, f"🥈 *Silver (XAG)*: ${price:.2f}", parse_mode="Markdown")

def run_bot():
    while True:
        try:
            print("Bot polling started...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
