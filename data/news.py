import requests


def get_news():
    url = 'https://newsapi.org/v2/top-headlines?country=ru&' \
          'apiKey=5f80be67653d478e82094179730f4798'
    r = requests.get(url)
    news = list(map(lambda el: (el['title'], el['description']),
                     r.json()['articles']))
    return news
