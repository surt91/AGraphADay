#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "You need 2 arguments: input and output file"
fi

IN=$1
OUT=$2
TMP=$1.tmp.png
BG=$1.bg.png

# twitters Android stream has 1.8:1 pictures (2048x1137)
# but twitter web seems to have 2:1          (2048x1024)
# it is probably better to crop left/right in android than up/down in web
X=2048
Y=1024
border=5%x5%

# we will add a transparent border of 1px. this way twitter will not convert
# it to jpg and add compression artifacts
# here, we account for the extra 2 pixels in both directions
X=$((X-2))
Y=$((Y-2))

# get background color
color="$(convert "$IN" -format "%[pixel:p{1,1}]" info:)"

if [[ "$IN" == *.svg ]]
then
    # trim, raster and resize the image
    convert -density 1000 -trim "$IN" -bordercolor "$color" -border "$border" +repage -rotate "-90<" -resize "$X"x"$Y" "$TMP"
else
    # trim and resize the image
    convert -trim "$IN" -bordercolor "$color" -border "$border" +repage -rotate "-90<" -resize "$X"x"$Y" "$TMP"
fi

# create background, this way we will always get the same aspect ratio
convert -size "$X"x"$Y" canvas:"$color" -alpha on -channel RGBA -bordercolor "rgba(0,0,0,0)" -border "1x1" "$BG"

# place the graph in the center of the background
composite -gravity center "$TMP" "$BG" "$OUT"

# compress more
#optipng -o7 "$OUT"

rm "$BG" "$TMP"
