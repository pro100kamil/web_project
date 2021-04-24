from datetime import datetime
import vk_api

from .config import VK_LOGIN, VK_PASSWORD

PATTERN_IN = "%Y-%m-%dT%H:%M:%SZ"

VK_SESSION = vk_api.VkApi(login=VK_LOGIN, password=VK_PASSWORD)
try:
    VK_SESSION.auth(token_only=True)
except vk_api.AuthError as error:
    print(error)
    exit(0)

VK = VK_SESSION.get_api()

cur_page, last_page = None, 1


def get_latest(max_results=10, query='', page=1):
    global last_page, cur_page

    params = {'q': query, 'adult': 1, 'offset': max_results * (page - 1),
              'count': max_results * page, 'filters': 'youtube,mp4', 'sort': 1}

    response = VK.video.search(**params)
    # print(response)
    videos = []
    for video in response['items']:
        url_img = ''
        for res in ['photo_130', 'photo_320', 'photo_640', 'photo_800'][::-1]:
            if video.get(res):
                url_img = video.get(res)
                break

        data = {'id': video['id'], 'oid': video['owner_id'],
                'title': video['title'],
                'description': video['description'], 'url_img': url_img,
                'date': datetime.utcfromtimestamp(video['date'])}

        videos += [data]

    return videos


def get_by_id(video_url: str):
    _, owner_id = video_url.split('_')

    params = {'owner_id': owner_id, 'videos': video_url, 'count': 1,
              'fields': 'image'}

    response = VK.video.get(**params)

    if response:
        v = response['items'][0]
        print(v)
        video = {'id': v['id'], 'title': v['title'],
                 'description': v['description'],
                 'url_img': v['image']['url'],
                 'date': datetime.utcfromtimestamp(v['date']),
                 'url_iframe': v['player']}

        return video

    return {}

# print(get_latest(query='плавание'))
# print(get_by_id('kcNpBNpvyc4'))
# for i in a:
#     print(i)
#     print()
