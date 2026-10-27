### steganography file extraction #stego

`binwalk -e <file>`

### stego password protected file

first verify there is something `steghide info cute-alien.jpg`

then extract it `steghide extract -sf cute-alien.jpg`

### Grabbing Frames From A Video

`ffmpeg -i myvideo.mp4 img%06d.png -hide_banner`
