from requests import get
import os
from dotenv import load_dotenv
from datetime import datetime

PATTERN_IN = "%Y-%m-%dT%H:%M:%SZ"
API_YOUTUBE_SERVER = 'https://www.googleapis.com/youtube/v3/search'

path = os.path.join(os.path.dirname(__file__), '../.env')
if os.path.exists(path):
    load_dotenv(path)

    YT_API_KEY = os.environ.get('YOUTUBE_API_KEY')

cur_page, last_page = None, 1


def get_latest(max_results=10, query='', page=1):
    global last_page, cur_page

    params = {'part': 'snippet', 'q': query, 'key': YT_API_KEY, 'type': 'video',
              'regionCode': 'ru', 'maxResults': max_results}

    if cur_page is None:
        response = get(API_YOUTUBE_SERVER, params=params).json()
        cur_page = response.get('pageToken')

    if page > last_page:
        for p in range(last_page, page):
            params['pageToken'] = cur_page
            response = get(API_YOUTUBE_SERVER, params=params).json()
            cur_page = response['nextPageToken']
    elif page < last_page:
        for p in range(last_page - 1, page, -1):
            params['pageToken'] = cur_page
            response = get(API_YOUTUBE_SERVER, params=params).json()
            cur_page = response['prevPageToken']

    last_page = page

    params['pageToken'] = cur_page
    response = get(API_YOUTUBE_SERVER, params=params).json()

    videos = []
    print(response)
    for v in response['items']:
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
        url_iframe = f"https://www.youtube.com/embed/{v['id']}"
        video = {'id': v['id'], 'title': v['snippet']['title'],
                 'description': v['snippet']['description'],
                 'url_img': v['snippet']['thumbnails']['medium']['url'],
                 'date': datetime.strptime(v['snippet']['publishedAt'], PATTERN_IN),
                 'url_iframe': url_iframe}
        return video

    return {}

# print(get_latest(query='плавание'))
# print(get_by_id('kcNpBNpvyc4'))
# for i in a:
#     print(i)
#     print()
