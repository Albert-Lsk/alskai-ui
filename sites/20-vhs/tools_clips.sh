#!/bin/sh
# Cut the PD source films into small, seek-friendly H.264 clips for the WebGL tape deck.
# Sources (src-img/, gitignored): Méliès 1902 480p transcode, NASA AS-506 film (both via Wikimedia Commons).
set -e
cd "$(dirname "$0")"
ENC="-an -c:v libx264 -preset slow -crf 31 -pix_fmt yuv420p -g 12 -movflags +faststart"
VF="scale=384:288:flags=lanczos,hqdn3d=1.5:1.5:4:4"
# Méliès reel: moon approach, comet + stars, fall into the sea (three chapters, 40 s)
ffmpeg -y -v error -i src-img/melies-480p.webm -filter_complex \
 "[0:v]trim=361:376,setpts=PTS-STARTPTS[a];[0:v]trim=446:458,setpts=PTS-STARTPTS[b];[0:v]trim=666:679,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1,$VF,format=gray,format=yuv420p" \
 $ENC img/melies.mp4
# Apollo 11 lift-off, colour (13 s); source is 640x484, crop to 4:3
ffmpeg -y -v error -ss 0.5 -t 13 -i src-img/apollo-as506.ogv -vf "crop=640:480,fps=24,$VF" $ENC img/apollo.mp4
# poster frames for no-WebGL / reduced-motion fallback
ffmpeg -y -v error -ss 13.6 -i img/melies.mp4 -frames:v 1 -q:v 4 img/melies-poster.jpg
ffmpeg -y -v error -ss 6 -i img/apollo.mp4 -frames:v 1 -q:v 4 img/apollo-poster.jpg
ls -la img
