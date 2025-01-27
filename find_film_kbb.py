import requests
from bs4 import BeautifulSoup
import re

site = requests.get('https://2016.kinofest.org/movie-theater')

if site.status_code == 200:
    html = site.text
    soup = BeautifulSoup(html, 'lxml')

def find_f():
    direc_films = soup.find_all(class_=re.compile(r'^mix cat-Онлайн-кинотеатр'))
    titles = [title.get('data-title') for title in direc_films]
    links = ['https://2016.kinofest.org/movie-theater' + link.find('a', class_='mix-title')['href'] for link in direc_films]
    return titles, links
