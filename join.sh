#!/bin/bash
# Join per-shot MP4s (concat demuxer, stream copy) and mux with the loudnormed mix.
# Produces: video.mp4 (silent join) and myheritage-final.mp4 (video + audio).
set -e
cd "$(dirname "$0")"
ls shots/*.mp4 | sort | sed "s/^/file '/; s/$/'/" > /tmp/mh_concat.txt
ffmpeg -v error -y -f concat -safe 0 -i /tmp/mh_concat.txt -c copy video.mp4
ffmpeg -v error -y -i video.mp4 -i audio/mix.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 256k -shortest myheritage-final.mp4
echo "final:"; ffprobe -v error -show_entries format=duration,size -of default=nw=1 myheritage-final.mp4
