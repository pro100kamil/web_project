from requests import get
import os
from dotenv import load_dotenv
from datetime import datetime


path = os.path.join(os.path.dirname(__file__), '../.env')

if os.path.exists(path):
    load_dotenv(path)

    YT_API_KEY = os.environ.get('YOUTUBE_API_KEY')

PATTERN_IN = "%Y-%m-%dT%H:%M:%SZ"


def get_latest(max_results=5, query=''):
    params = {'part': 'snippet', 'q': query, 'key': YT_API_KEY, 'type': 'video',
              'regionCode': 'ru', 'maxResults': max_results}
    response = get('https://www.googleapis.com/youtube/v3/search', params=params).json()['items']

    videos = []
    for v in response:
        _dict = {'id': v['id']['videoId'], 'title': v['snippet']['title'],
                 'description': v['snippet']['description'],
                 'url_img': v['snippet']['thumbnails']['medium']['url'],
                 'date': datetime.strptime(v['snippet']['publishedAt'], PATTERN_IN)}
        videos += [_dict]

    return videos


def get_by_id(video_id):
    params = {'part': 'snippet', 'key': YT_API_KEY, 'id': video_id}
    response = get('https://www.googleapis.com/youtube/v3/videos', params=params).json()['items']

    if response:
        v = response[0]
        video = {'id': v['id'], 'title': v['snippet']['title'],
                 'description': v['snippet']['description'],
                 'url_img': v['snippet']['thumbnails']['medium']['url'],
                 'date': datetime.strptime(v['snippet']['publishedAt'], PATTERN_IN)}
        return video

    return {}


# print(get_latest(query='плавание'))
print(get_by_id('kcNpBNpvyc4'))
# for i in a:
#     print(i)
#     print()
