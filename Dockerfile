FROM python:3.12-alpine

WORKDIR /usr/src/app

COPY . .

# 合并多个RUN命令到一个，并清理安装时产生的缓存
RUN	apk add --no-cache git aria2 ffmpeg && \
ln -s /root /app && \
aria2c https://github.com/yt-dlp/yt-dlp/releases/download/2024.08.06/yt-dlp_linux -o yt-dlp && \
mv yt-dlp /usr/bin && \
chmod +x /usr/bin/yt-dlp && \
pip install --no-cache-dir -r requirements.txt && \
rm -rf /var/cache/apk/

CMD [ "python", "bili-sync-yt-dlp.py" ]
