#!/bin/bash

# 切换到存放视频和音频文件的目录
cd "/视频存放路径"

# 递归遍历所有子目录和文件
find . -type f -name "*.mp4" | while read -r video; do
  # 提取视频文件的基础名称（去掉 ".f" 和扩展名）
  base_name="${video%.f*.mp4}"
  echo "基础名称: $base_name"
  
  # 使用通配符展开匹配的音频文件
  audio_files=("${base_name}.f"*.m4a)
  
  # 检查是否找到匹配的音频文件
  if [[ -f "${audio_files[0]}" ]]; then
    audio_file="${audio_files[0]}"
    echo "找到的音频文件: $audio_file"
    
    # 构建合并后的文件名，删除 "]" 到 ".mp4" 之间的内容
    output_file="${base_name%f*}.mp4"
    
    echo "合并视频: $video 和音频: $audio_file -> $output_file"
    
    # 使用ffmpeg合并音视频
    ffmpeg -i "$video" -i "$audio_file" -c copy "$output_file"
    
    # 检查ffmpeg命令是否成功
    if [[ $? -eq 0 ]]; then
      # 删除原始视频和音频文件
      rm "$video" "$audio_file"
      echo "已删除原始视频和音频文件: $video 和 $audio_file"
    else
      echo "合并失败，保留原始文件: $video 和 $audio_file"
    fi
  else
    echo "跳过: 未找到对应音频文件 for $video"
  fi
done
