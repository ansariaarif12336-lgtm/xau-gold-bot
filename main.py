import os, threading, requests
from flask import Flask
import telebot

TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running! OK"

if TOKEN:
    bot = telebot.TeleBot(TOKEN)
    @bot.message_handler(commands=['start'])
    def start(m):
        bot.reply_to(m, "Gold Scalp Bot Active! Use /paxg")
    @bot.message_handler(commands=['paxg'])
    def paxg(m):
        try:
            r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=pax-gold&vs_currencies=usd", timeout=10).json()
            bot.reply_to(m, f"XAU / PAXG: ${r['pax-gold']['usd']} USD")
        except Exception as e:
            bot.reply_to(m, f"Error: {e}")
    def run_bot():
        bot.infinity_polling()
    threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
