FROM python:3.12-alpine

WORKDIR /usr/src/app

COPY . .

# 合并多个RUN命令到一个，并清理安装时产生的缓存
RUN	apk add --no-cache git aria2 ffmpeg && \
ln -s /root /app && \
# 原来使用aria2下载yt-dlp，后出现问题改用pip安装特定版本
# aria2c https://github.com/yt-dlp/yt-dlp/releases/download/2024.11.18/yt-dlp_linux -o yt-dlp && \
# ln -s yt-dlp /usr/bin && \
# chmod +x yt-dlp && \
pip install --no-cache-dir -r requirements.txt && \
rm -rf /var/cache/apk/

CMD [ "python", "bili-sync-yt-dlp.py" ]
