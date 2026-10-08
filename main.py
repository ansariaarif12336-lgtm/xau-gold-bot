import telebot
import requests
import threading
import time
from flask import Flask

BOT_TOKEN = "APNA_BOT_TOKEN_YAHAN_DALO"  # <-- yahan apna token daal dena
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Live!"

def get_paxg_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=pax-gold&vs_currencies=usd"
        r = requests.get(url, timeout=10).json()
        return r['pax-gold']['usd']
    except:
        return None

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "Gold Scalp Robot Live! 🚀\n/paxg - Gold Price\n/xau - Gold Price\n/xag - Silver")

@bot.message_handler(commands=['paxg','xau','xag'])
def price(m):
    p = get_paxg_price()
    if p:
        bot.reply_to(m, f"XAU / PAXG: ${p} USD\nSource: CoinGecko")
    else:
        bot.reply_to(m, "Price fetch failed, try again")

def run_bot():
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
