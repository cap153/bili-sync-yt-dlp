from time import sleep
from os import path,makedirs
from re import sub as sub
from subprocess import CalledProcessError, run as subprocess_run
from asyncio import run as asyncio_run
from toml import load
from bilibili_api import Credential,video,favorite_list,settings
from load_data import SQLiteManager

# settings.proxy = "http://192.168.1.5:2080" # 里头填写你的代理地址
settings.timeout = 300.0 # 超时时间设置久一点
# 读取配置文件
with open(path.expanduser("~/.config/bili-sync/config.toml"), 'r', encoding='utf-8') as f:
    bili_sync_config = load(f)
# 收藏夹的id列表
media_id_list = list(bili_sync_config['favorite_list'].keys())
# 间隔时间
interval = bili_sync_config['interval']
# 用于身份认证,window.localStorage.ac_time_value
credential = Credential(sessdata=bili_sync_config['credential']['sessdata'], bili_jct=bili_sync_config['credential']['bili_jct'], buvid3=bili_sync_config['credential']['buvid3'], dedeuserid=bili_sync_config['credential']['dedeuserid'], ac_time_value=bili_sync_config['credential']['ac_time_value'])
# 需要下载的视频
need_download_bvids = dict()

async def get_bvids(media_id):
    """
    获取收藏夹下面的所有视频bvid，如果有未下载的新视频会更新字典

    :param media_id: 收藏夹id
    """
    # 实例化 FavoriteList 类，用于获取指定收藏夹信息
    fav_list = favorite_list.FavoriteList(media_id = media_id,credential = credential)
    try:
        ids = await fav_list.get_content_ids_info()
    except Exception as e:
        print(f"发生错误: {e}，下一轮重试")
        return
    for id in ids:
        # 未下载的新视频更新字典
        if id['bvid'] not in already_download_bvids(media_id).copy():
            need_download_bvids[media_id].add(id['bvid'])

async def get_video_info(media_id,bvid):
    """
    获取视频信息。

    :param media_id: 收藏夹id
    :param bvid: 视频bvid

    Returns:
        dict: title的值为视频标题，pages为视频分p信息，如果pages的长度大于1表示存在多分p
    """
    # 实例化 Video 类，用于获取指定视频信息
    v = video.Video(bvid=bvid, credential=credential)
    # 获取视频信息
    info = dict()
    try:
        info['title'] = (await v.get_info())['title']
        info['pages'] = len((await v.get_info())['pages'])
        info['dynamic'] = (await v.get_info())['dynamic'] 
    except Exception:
        # 失效的视频添加到已经下载集合
        already_download_bvids_add(media_id=media_id,bvid=bvid)
        print(bvid+"视频失效")
    return info

def download_video(media_id,bvid,download_path):
    """
    使用 yt-dlp 下载视频。

    :param media_id: 收藏夹的id
    :param bvid: 视频的bvid
    :param download_path: 存放视频的文件夹路径
    """
    video_url = "https://www.bilibili.com/video/"+bvid # 使用bvid拼接出视频的下载地址
    command = [
        "yt-dlp", # 调用yt-dlp已经下载的视频会自动跳过
        "-f", "bestvideo+bestaudio/best",video_url, # 最高画质下载视频
        "--write-thumbnail", # 下载视频的缩略图或海报图片并保存为单独的文件
        # "--embed-thumbnail" # 先下载缩略图或海报图片，并将它嵌入到视频文件中（如果视频格式支持），需要ffmpeg
        "--external-downloader", "aria2c", # 启用aria2，将支持aria2的特性断点续传和多线程
        "--external-downloader-args", "-x 16 -k 1m", # aria2线程等参数设置
        "--cookies", path.expanduser("~/.config/bili-sync/cookies.txt"), # cookies读取
        "-P", download_path, # 指定存放视频的文件夹路径
        "--restrict-filenames", # 自动限制文件名中的字符，使其符合文件系统的要求
        "-o", "%(title).50s [%(id)s].%(ext)s" # 限制文件名称长度
    ]
    try:
        subprocess_run(command, check=True)
        # 下载成功，更新字典数据
        already_download_bvids_add(media_id=media_id,bvid=bvid)
        print(f"[info] {download_path} 下载成功")
    except CalledProcessError:
        print(f"[error] {download_path} 下载失败")

# 把bili-sync配置文件中的cookies信息保存为yt-dlp可以识别的格式
def save_cookies_to_txt():
    # 获取cookies信息
    cookies = bili_sync_config.get('credential', {})
    # 创建yt-dlp识别的cookies格式
    cookies_lines = [
        f"# Netscape HTTP Cookie File",
        f"# This is a generated file! Do not edit.",
        "",
    ]
    for name, value in cookies.items():
        if value:
            cookies_lines.append(f".bilibili.com\tTRUE\t/\tFALSE\t0\t{name.upper()}\t{value}")
    # 保存到cookies.txt文件
    with open(path.expanduser("~/.config/bili-sync/cookies.txt"), 'w', encoding='utf-8') as f:
        f.write("\n".join(cookies_lines))

# 数据库读取已经下载的视频bvids
def already_download_bvids(media_id):
    with SQLiteManager(path.expanduser("~/.config/bili-sync/data.sqlite3")) as db_manager:
        return db_manager.get_values(table_name=media_id)

# 数据库添加下载成功的视频
def already_download_bvids_add(media_id,bvid):
    with SQLiteManager(path.expanduser("~/.config/bili-sync/data.sqlite3")) as db_manager:
        db_manager.insert_data(table_name=media_id,value=bvid)

# 初始化
def init_download():
    # 把bili-sync配置文件中的cookies信息保存为yt-dlp可以识别的格式
    save_cookies_to_txt() 
    # 根据收藏夹id初始化字典数据
    for media_id in media_id_list:
        need_download_bvids.setdefault(media_id, set())

# 间隔指定时间检查收藏夹是否更新并下载
def check_updates_download():
    while True:
        for media_id in media_id_list:
            # 根据收藏夹id读取配置文件中的保存路径
            download_path = bili_sync_config['favorite_list'][media_id]
            # 获取收藏夹中未下载的视频的bvid
            asyncio_run(get_bvids(media_id))
            # 获取未失效的视频信息并下载
            for bvid in need_download_bvids[media_id].copy(): # 遍历的时候使用copy()方法创建副本，这样即使在迭代过程中修改了原集合，也不会影响到迭代器
                video_info = asyncio_run(get_video_info(media_id,bvid)) # 获取视频信息
                if len(video_info)>0: # 仅下载可以获取到信息的视频
                    video_name = video_info['title']
                    # 定义视频文件夹路径
                    video_dir = path.join(download_path, video_name)
                    # 判断文件夹是否存在，不存在则创建
                    if not path.exists(video_dir):
                        makedirs(video_dir)
                    download_video(media_id,bvid,video_dir)
            # 对比已经下载的数据批量更新需要下载的数据
            for bvid in already_download_bvids(media_id):
                try: # 如果need_download_bvids不存在该bvid表示已经更新过数据，直接跳过
                    need_download_bvids[media_id].remove(bvid)
                except KeyError:
                    pass
        print(f"[info] {interval}秒后执行下一轮")
        sleep(interval)

if __name__ == "__main__":
    init_download() # 第一次运行同步本地已经下载的视频信息
    check_updates_download() # 后续只下载收藏夹新增视频和之前下载失败的视频
