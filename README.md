# 爱发电播客下载
**前排提醒：本工具仅能下载已赞助的节目，白嫖就别想了**
## 使用
首先需要从cookies里获取`auth_token`，方法有很多，个人推荐拓展[Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)。

```shell
$ git clone git@github.com:senventise/afdian_podcast_down.git
$ cd afdian_podcast_down
$ auth_token="YOUR_TOKEN" python main.py
```
有可能需要`ffmpeg`
