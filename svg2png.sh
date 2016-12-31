#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "You need 2 arguments: input and output file"
fi

IN=$1
OUT=$2
TMP=tmp.png
BG=bg.png

# twitters Android stream has 1.8:1 pictures (2048x1137)
# but twitter web seems to have 2:1          (2048x1024)
# it is probably better to crop left/right in android than up/down in web
X=2048
Y=1024
border=5%x5%

# get background color
color="$(convert "$IN" -format "%[pixel:p{1,1}]" info:)"

# trim, raster and resize the image
convert -density 1000 -trim "$IN" -bordercolor "$color" -border "$border" +repage -resize "$X"x"$Y" -rotate "-90<" "$TMP"

# create background, but add 1% transaprency to top left pixel
# this way twitter should not convert the png into a jpg full of artifacts
convert -size "$X"x"$Y" canvas:"$color" -alpha on -channel RGBA -fx "i==0&&j==0?$(echo $color | sed 's/)/,0.99)/' | sed 's/[s]rgb[a]/rgba/'):u" "$BG"

# place the graph in the center of the background
composite -gravity center "$TMP" "$BG" "$OUT"

# compress more
optipng -o7 "$OUT"

rm "$BG" "$TMP"

