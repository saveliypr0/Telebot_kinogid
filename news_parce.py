import requests
from bs4 import BeautifulSoup
import re


conn_news = requests.get("https://2016.kinofest.org/news")


def show_news(page):
    if conn_news.status_code == 200:
        html = conn_news.text
        soup = BeautifulSoup(html, 'lxml')
        all_news = soup.find_all(class_="nspArt nspCol4")

        hyperlink = all_news[page].find('a')['href']
        img_tag = all_news[page].find('img')
        text_news = all_news[page].text.replace('Читать далее',
                                                f"<a href='https://2016.kinofest.org{hyperlink}'>Читать далее</a>")

        text_news = re.sub(r"(\d{2}\.\d{2}\.\d{4})([^\n])", r"\1\n\2", text_news)

        return img_tag['src'], text_news
