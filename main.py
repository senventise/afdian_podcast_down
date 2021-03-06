import argparse
import os
from random import randint
from time import sleep

import eyed3
import requests

SLEEP_TIME = 30

cookies = {}

headers = {
    'authority': 'afdian.net',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    'afd-stat-id': '3006e2148b3111ecb5a452540025c377',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': 'https://afdian.net/album/c6ae1166a9f511eab22c52540025c377',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
}


def download_page(data, n: int=-1):
    albums = data["list"]
    for album in albums:
        # 下载n期
        if not n == -1:
            if n > 0:
                n -= 1
            elif n == 0:
                break
        else:
            print("下载全部")
        title = album["title"]
        author = album["user"]["name"]
        description = album["content"]
        cover_url = album["audio_thumb"]
        audio_url: str = album["audio"]
        filename = f"{title}.mp3"
        print(f"正在处理：{title}")
        if audio_url.strip() == "":
            print("本条动态没有音频文件，跳过")
            continue
        cover = None
        try:
            cover = requests.get(cover_url).content
            print(f"封面下载完毕")
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
            print(f"已完成\n")
        except Exception as e:
            print("下载歌曲失败")
            print(e)
        sleep(SLEEP_TIME + randint(0, 5))


def get_all_albums(album_id: str):
    params = {
        'album_id': album_id,
        'lastRank': 0,
        'rankOrder': 'asc',
        'rankField': 'publish_sn',
    }
    while True:
        resp = requests.get('https://afdian.net/api/user/get-album-post', headers=headers, params=params,
                            cookies=cookies).json()
        data = resp["data"]
        download_page(data)
        params["lastRank"] += 10
        sleep(SLEEP_TIME + randint(0, 5))
        if data["has_more"] == 0:
            # 遍历完毕
            break


# 获取倒数第n期节目
def get_latest_n(album_id: str, n=0):
    params = {
        'album_id': album_id,
        'lastRank': 0,
        'rankOrder': 'desc',
        'rankField': 'publish_sn',
    }
    resp = requests.get('https://afdian.net/api/user/get-album-post', headers=headers, params=params,
                        cookies=cookies).json()
    data = resp["data"]
    #print(data["list"])
    print("="*50)
    download_page(data, n)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="爱发电播客下载")
    parser.add_argument("--id", required=True, type=str, help="URL里的id")
    parser.add_argument("--all", action="store_true", help="下载全部")
    parser.add_argument("--latest", metavar="n", type=int, default=1, help="下载最新n期")
    args = parser.parse_args()
    if "auth_token" in os.environ:
        cookies["auth_token"] = os.environ["auth_token"]
    else:
        print("auth_token未配置")
        exit(1)
    if args.all:
        get_all_albums(args.id)
    if args.latest:
        get_latest_n(args.id, args.latest)
