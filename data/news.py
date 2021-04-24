import requests


def get_news() -> list:
    url = 'https://newsapi.org/v2/top-headlines?country=ru&' \
          'apiKey=5f80be67653d478e82094179730f4798'
    r = requests.get(url)
    news = list(map(lambda el: (el['title'], str(el['description']), el['url'],
                                str(el['urlToImage'])),
                    r.json()['articles']))
    return news
