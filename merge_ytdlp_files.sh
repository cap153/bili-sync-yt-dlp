#!/bin/bash

# 切换到存放视频和音频文件的目录
cd "/home/captain/media" || exit 1

# 使用find命令获取所有音频和视频文件路径并存储到数组中
mapfile -t audio_files < <(find . -type f -name "*.m4a")
mapfile -t video_files < <(find . -type f -name "*.mp4")

# 遍历所有音频文件
for audio in "${audio_files[@]}"; do
  # 提取音频文件的基础名称（去掉扩展名）
  base_name="${audio%.f*.m4a}"
  
  # 查找匹配的的视频文件
  for video in "${video_files[@]}"; do
    # 提取视频文件的基础名称（去掉扩展名）
    video_base_name="${video%.f*.mp4}"
    
    # 比较基础名称
    if [[ "$base_name" == "$video_base_name" ]]; then
      # 构建合并后的文件名
      output_file="${base_name##*/}.mp4"  # 仅保留文件名部分，去掉路径
      
      echo "合并视频: $video 和音频: $audio -> $output_file"
      
      # 使用ffmpeg合并音视频
      if ffmpeg -i "$video" -i "$audio" -c copy -shortest "$output_file"; then
        # 删除原始视频和音频文件
        rm "$video" "$audio"
        echo "已删除原始视频和音频文件: $video 和 $audio"
      else
        echo "合并失败，保留原始文件: $video 和 $audio"
      fi
      
      # 处理完一个匹配文件后跳出内层循环，避免重复处理
      break
    fi
  done
done
