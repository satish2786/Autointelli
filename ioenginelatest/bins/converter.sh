#!/bin/bash

mkdir -p /usr/share/nginx/html/downloads/videos;
mkdir -p /usr/share/nginx/html/downloads/video_bkp;
cd /usr/share/nginx/html/downloads/videos;

files=$(ls -l | grep -v -e "\.mp4" -e "\.m4v" -e "\.sh" | awk '{print $9}');

for i in $files;
do

echo "converting $i";

/usr/local/bin/guacenc $i && echo "converted $i to m4v" || continue;
sleep 5;

/usr/bin/ffmpeg -i "$i.m4v" "$i.mp4";
sleep 5;

if [[ -e "$i.m4v" && -e "$i.mp4" ]]
then
  mv $i ../video_bkp/;
  mv "$i.m4v" ../video_bkp/;
else
  echo "gets converted next time";
fi;

done;
