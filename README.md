# 使用方法

Linux/amd64 与 Linux/arm64 两个平台可直接使用 Docker 或 Docker Compose 运行，此处以 Compose 为例：

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
```

- `interval`:表示程序每次执行扫描下载的间隔时间，单位为秒。
- `credential`:哔哩哔哩账号的身份凭据，请参考凭据获取[流程获取](https://nemo2011.github.io/bilibili-api/#/get-credential)并对应填写至配置文件中，后续 bili-sync 会在必要时自动刷新身份凭据，不再需要手动管理。推荐使用匿名窗口获取，避免潜在的冲突。
- `favorite_list`:你想要下载的收藏夹与想要保存的位置。简单示例：

```bash
3115878158 = "/home/amtoaer/Downloads/bili-sync/测试收藏夹"
```

# 目录结构

1. 单页视频

```bash
├── {video_name}
│   ├── {video_name}.mp4
│   └── {pvideo_name}.jpg
```

2. 多页视频和互动视频

```bash
├── {video_name}
│   ├── Season 1
│   │   ├── {video_name} {page_name}.mp4
│   │   ├── {video_name} {page_name}.jpg
│   │   ├── {video_name} {page_name}.mp4
│   │   └── {video_name} {page_name}.jpg
```
