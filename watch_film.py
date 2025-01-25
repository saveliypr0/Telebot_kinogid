import telebot
import requests
from bs4 import BeautifulSoup
from logicbot import BOT_TOKEN

bot = BOT_TOKEN


@bot.callback_query_handler(func=lambda callback: callback.data.startswith("watch_"))
def watch(callback):
    movie_name = callback.data.split("_")[1]
    site_re = requests.get("https://2025.lordfilm-ttv.ru/")

    if site_re.status_code == 200:
        html = site_re.text
        soup = BeautifulSoup(html, 'lxml')
        parce_film = soup.find_all()
