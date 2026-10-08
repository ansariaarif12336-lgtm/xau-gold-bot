import os
import threading
import requests
from flask import Flask
import telebot

TOKEN = os.getenv("BOT_TOKEN")
print(f"TOKEN FOUND: {bool(TOKEN)}", flush=True)

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

@app.route('/')
def home():
    return "Bot is Running! OK"

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "Gold Scalp Bot Active! Use /paxg")

@bot.message_handler(commands=['paxg'])
def paxg(m):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=pax-gold&vs_currencies=usd"
        r = requests.get(url, timeout=10).json()
        price = r['pax-gold']['usd']
        bot.reply_to(m, f"XAU / PAXG: ${price} USD")
    except Exception as e:
        bot.reply_to(m, f"Error: {e}")

def run_bot():
    print("Starting Bot...", flush=True)
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def start_flask():
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

start_flask()
