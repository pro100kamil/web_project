from requests import get
from bs4 import BeautifulSoup


def latest_news(channel_name):
    kol = 5
    tg_url = 'https://t.me/s/'
    url = tg_url + channel_name
    r = get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    url = soup.find_all('a')[-1]['href'].replace('https://t.me/', '')
    channel_name, news_id = url.split('/')
    news_id = int(news_id)
    urls = []
    for i in range(min(kol, news_id)):
        urls.append(f'{channel_name}/{news_id - i}')
    return urls
