import requests
from bs4 import BeautifulSoup


site = requests.get('https://2016.kinofest.org/movie-theater')

if site.status_code == 200:
    html = site.text
    soup = BeautifulSoup(html, 'lxml')

def find_f():
    all_films = soup.find_all(class_="inner-mix bottom-mix")
    return all_films

def photo_film():
    photo = soup.find_all(class_="upper-mix")
    return photo
