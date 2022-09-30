# 爱发电播客下载
**前排提醒：本工具仅能下载正在发电的节目**
## 使用
注意：有可能需要`ffmpeg`
```shell
$ git clone git@github.com:senventise/afdian_podcast_down.git
$ cd afdian_podcast_down
```
### 获取 album_id  
节目的url应为：`https://afdian.net/album/ALBUM_ID`, 注意是节目的url, 不是创作者的。 
### 获取 auth_token  
推荐使用浏览器拓展 [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) 获取cookie中的 `auth_token`
### 下载全部
```shell
$ auth_token="AUTH_TOKEN" python main.py --id ALBUM_ID --all
```
### 下载最新n期
```shell
# 列出最新n期
$ auth_token="AUTH_TOKEN" python main.py --id ALBUM_ID --latest n --list
# 下载
$ auth_token="AUTH_TOKEN" python main.py --id ALBUM_ID --latest n
```
