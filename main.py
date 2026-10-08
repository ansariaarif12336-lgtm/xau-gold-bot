import os, time, requests
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
CACHE = {"price": None, "time": 0}

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Running!"
def run_web(): app.run(host='0.0.0.0', port=10000)

def get_gold_price():
    if time.time() - CACHE["time"] < 300 and CACHE["price"]:
        return CACHE["price"]
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=pax-gold&vs_currencies=usd"
        r = requests.get(url, timeout=10)
        price = r.json()['pax-gold']['usd']
        CACHE["price"] = price
        CACHE["time"] = time.time()
        return price
    except:
        return CACHE["price"] or 2650.0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Gold Bot Ready! Use /paxg , /xau , /gold")

async def paxg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_gold_price()
    text = f"🪙 PAXG / XAU Gold Price\n\n💰 Price: ${price:,.2f}\n📈 Live Market"
    await update.message.reply_text(text)

if __name__ == '__main__':
    Thread(target=run_web).start()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("paxg", paxg))
    application.add_handler(CommandHandler("xau", paxg))
    application.add_handler(CommandHandler("gold", paxg))
    application.run_polling()
