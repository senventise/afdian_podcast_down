import argparse
import os
from random import randint, random
from time import sleep

import eyed3
import requests

SLEEP_TIME = 30
AFDIAN_DOMAIN = 'ifdian.net'

cookies = {}

headers = {
    'authority': AFDIAN_DOMAIN,
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': f'https://{AFDIAN_DOMAIN}/album/c6ae1166a9f511eab22c52540025c377',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
}


def download_page(albums, list_only: bool, n: int=-1):
    for album in albums:
        # 下载n期
        if not n == -1:
            if n > 0:
                n -= 1
            elif n == 0:
                break
        title = album["title"]
        author = album["user"]["name"]
        description = album["content"]
        cover_url = album["audio_thumb"]
        audio_url: str = album["audio"]
        # 是否仅列出
        if list_only:
            print(title)
            print(description.replace("\n\n", "\n")) # 去除多余空行
            print("="*40)
        else:
            filename = f"{title}.mp3"
            print(f"正在处理：{title}")
            if audio_url.strip() == "":
                print("本条动态没有音频文件，跳过")
                continue
            cover = None
            try:
                cover = requests.get(cover_url).content
                print("封面下载完毕")
            except Exception as e:
                print(f"封面下载失败：{cover_url}")
                print(e)
            try:
                if not os.path.exists(filename):
                    # 没有下载过
                    mp3 = requests.get(audio_url, headers=headers, cookies=cookies).content
                    with open(filename, "wb+") as file:
                        file.write(mp3)
                    print(f"{filename} 下载完成")
                audio: eyed3.core.AudioFile = eyed3.load(filename)
                if audio is None and os.path.exists(filename):
                    # 不知道为什么有些是ISO Media, MP4 Base Media v1，eyed3识别不了
                    print("不支持的音频格式，转码中")
                    # 使用ffmpeg转码
                    if os.system(f"ffmpeg -i \"{filename}\" \"{filename}.mp3\"") == 0:
                        os.remove(filename)
                        os.rename(f"{filename}.mp3", f"{filename}")
                    else:
                        print("转码出错")
                        continue
                audio: eyed3.core.AudioFile = eyed3.load(filename)
                if audio.tag is None:
                    audio.initTag()
                audio.tag.artist = author
                audio.tag.title = title
                audio.tag.album = title
                audio.tag.comments.set(description)
                audio.tag.images.set(3, cover, "image/jpeg")
                audio.tag.save()
                print("已完成\n")
            except Exception as e:
                print("下载歌曲失败")
                print(e)
            sleep(SLEEP_TIME + randint(0, 5))


def get_all_albums(album_id: str, list_only: bool):
    params = {
        'album_id': album_id,
        'lastRank': 0,
        'rankOrder': 'asc',
        'rankField': 'rank',
    }
    while True:
        resp = requests.get(f'https://{AFDIAN_DOMAIN}/api/user/get-album-post', headers=headers, params=params,
                            cookies=cookies).json()
        data = resp["data"]
        download_page(data, list_only, -1)
        params["lastRank"] += 10
        if list_only:
            sleep(randint(2, 5))
        else:
            sleep(SLEEP_TIME + randint(0, 5))
        if data["has_more"] == 0:
            # 遍历完毕
            break


def get_latest_n(album_id: str, n:int = 0) -> list:
    albums = []
    has_more = True
    params = {
        'album_id': album_id,
        'lastRank': 0,
        'rankOrder': 'desc',
        'rankField': 'publish_sn',
    }

    while len(albums) < n and has_more:
        resp = requests.get(f'https://{AFDIAN_DOMAIN}/api/user/get-album-post', headers=headers, params=params,
                        cookies=cookies).json()
        albums += resp["data"]['list']
        has_more = True if resp['data']['has_more'] == 1 else False
        params['lastRank'] = albums[-1]['rank']
        sleep(random())

    return albums[:n]


# 下载倒数n期节目
def download_latest_n(album_id: str, list_only: bool, n:int = 0):
    albums = get_latest_n(album_id, n)
    download_page(albums, list_only, n)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="爱发电播客下载")
    parser.add_argument("--id", required=True, type=str, help="URL里的id")
    parser.add_argument("--list", action="store_true", help="仅列出，不下载")
    parser.add_argument("--all", action="store_true", help="下载全部")
    parser.add_argument("--latest", metavar="n", type=int, default=1, help="下载最新n期")
    args = parser.parse_args()
    if "auth_token" in os.environ:
        cookies["auth_token"] = os.environ["auth_token"]
    else:
        print("auth_token未配置")
        exit(1)
    if args.all:
        get_all_albums(args.id, args.list)
    if args.latest:
        download_latest_n(args.id, args.list, args.latest)
