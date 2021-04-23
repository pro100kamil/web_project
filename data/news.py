import requests


def get_news() -> list:
    url = 'https://newsapi.org/v2/top-headlines?country=ru&' \
          'apiKey=5f80be67653d478e82094179730f4798'
    r = requests.get(url)
    print(r.json()['articles'][0]['urlToImage'])
    print(r.json()['articles'][0]['url'])
    news = list(map(lambda el: (el['title'], el['description'], el['url'],
                                el['urlToImage']),
                    r.json()['articles']))
    return news


get_news()
