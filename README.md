> 首次运行时，程序会扫描目录，并记录成功下载和现存的视频信息到`data.sqlite3`数据库文件中。该文件与配置文件存放于同一目录。若需重新扫描并记录所有视频，删除 data.sqlite3 文件后重新运行程序即可。

# 使用方法

【bili-sync-yt-dlp下载b站视频】 https://www.bilibili.com/video/BV1e9WVemEWV/?share_source=copy_web&vd_source=d34abe3786a6b85ecc07875a85795885

目前只有 Linux/amd64 平台可使用 Docker 或 Docker Compose 运行，其他平台请[自行编译](#Dockerfile编译运行)，此处以 Compose 为例：

```yml
services:
  bili-sync-yt-dlp:
    image: cap153/bili-sync-yt-dlp:latest
    restart: unless-stopped
    network_mode: bridge
    hostname: bili-sync-yt-dlp
    container_name: bili-sync-yt-dlp
    volumes:
      - ${你希望存储程序配置的目录}:/app/.config/bili-sync
      # 还需要有视频下载位置
      # 这些目录不是固定的，只需要确保此处的挂载与 bili-sync-yt-dlp 的配置文件相匹配
```

# 配置文件

当前版本的默认示例文件如下：

```toml
interval = 1200

[credential]
sessdata = ""
bili_jct = ""
buvid3 = ""
dedeuserid = ""
ac_time_value = ""

[favorite_list]
<收藏夹id> = "<保存的路径>"
<收藏夹id> = "<保存的路径>"
```

- `interval`:表示程序每次执行扫描下载的间隔时间，单位为秒。
- `credential`:哔哩哔哩账号的身份凭据，请参考凭据获取[流程获取](https://nemo2011.github.io/bilibili-api/#/get-credential)并对应填写至配置文件中，后续 bili-sync 会在必要时自动刷新身份凭据，不再需要手动管理。推荐使用匿名窗口获取，避免潜在的冲突。
- `favorite_list`:你想要下载的收藏夹与想要保存的位置。简单示例：

```bash
3115878158 = "/home/amtoaer/Downloads/bili-sync/测试收藏夹"
```
# 收藏夹id获取方法

[什么值得买的文章有详细介绍](https://post.smzdm.com/p/a4xl63gk/)，打开收藏夹

![image](https://github.com/user-attachments/assets/02efefe9-0a3a-46d6-8646-a6aa462d62c2)

浏览器可以看到“mlxxxxxxx”，只需要后面数字即可（不需要“ml“）

![image](https://github.com/user-attachments/assets/270c7f2f-b1b1-49a1-a450-a133f0d459fa)

# 目录结构

```bash
├── {video_name}
│   ├── {video_name} {page_name}.mp4
│   ├── {video_name} {page_name}.jpg
│   ├── {video_name} {page_name}.mp4
│   └── {video_name} {page_name}.jpg
```

# Dockerfile编译运行

```bash
# 下载最新源码
git clone --depth 1 https://github.com/cap153/bili-sync-yt-dlp
# 进入项目目录
cd bili-sync-yt-dlp
# 构建docker镜像
docker build -t bili-sync-yt-dlp ./
# 创建容器并运行，自行修改相关参数
docker run -it --restart=always --name bili-sync-yt-dlp  -v <配置文件路径>:/app/.config/bili-sync -v <视频想保存的路径>:<配置文件写的收藏夹路径> bili-sync-yt-dlp
```

# 源码运行

1. 安装ffmpeg并配置环境变量，[https://www.ffmpeg.org/](https://www.ffmpeg.org/)
2. 安装yt-dlp并配置环境变量，[https://github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp)
3. 安装aria2并配置环境变量，[https://github.com/aria2/aria2](https://github.com/aria2/aria2)
4. 安装python环境，开发使用的是python3.12
5. 配置文件请放在如下路径`~/.config/bili-sync/config.toml`

```bash
git clone --depth 1 https://github.com/cap153/bili-sync-yt-dlp
# 进入项目目录
cd bili-sync-yt-dlp
# 安装依赖
pip install -r requirements.txt
# 运行代码
python bili-sync-yt-dlp.py
```


