import os, time, requests
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running! UptimeRobot OK"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def get_gold_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=pax-gold&vs_currencies=usd"
        r = requests.get(url, timeout=10)
        return r.json()['pax-gold']['usd']
    except:
        return 4134.29

async def paxg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_gold_price()
    await update.message.reply_text(f"XAU / PAXG Price: ${price} USD\nSignal: Monitor 7-day low")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Gold Scalp Robot Active! Use /paxg")

def run_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("paxg", paxg))
    application.add_handler(CommandHandler("start", start))
    print("Bot polling started...")
    application.run_polling()

Thread(target=run_web, daemon=True).start()

if __name__ != "__main__":
    Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    Thread(target=run_bot, daemon=True).start()
    while True:
        time.sleep(3600)
