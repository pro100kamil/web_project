import requests
from .config import NEWS_API_KEY


def get_news() -> list:
    url = 'https://newsapi.org/v2/top-headlines?country=ru&' \
          f'apiKey={NEWS_API_KEY}'
    r = requests.get(url)
    news = list(map(lambda el: (el['title'], str(el['description']), el['url'],
                                str(el['urlToImage'])),
                    r.json()['articles']))
    return news
