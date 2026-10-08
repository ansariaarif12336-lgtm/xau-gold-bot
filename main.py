import os
import threading
import requests
from flask import Flask
import telebot

TOKEN = os.getenv("BOT_TOKEN")
print
