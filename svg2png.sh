#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "You need 2 arguments: input and output file"
fi

IN=$1
OUT=$2
TMP=tmp.png
BG=bg.png

# twitters Android stream has 1.8:1 pictures
X=2700
Y=1500
border=5%x5%

# get background color
color=$(convert "$IN" -format "%[pixel:p{1,1}]" info:)

# trim, raster and resize the image
convert -density 1000 -trim "$IN" -bordercolor "$color" -border "$border" +repage -resize "$X"x"$Y" -rotate "-90<" "$TMP"

convert -size "$X"x"$Y" canvas:"$color" "$BG"

# place the graph in the center of the background
composite -gravity center "$TMP" "$BG" "$OUT"

# compress more
optipng -o7 "$OUT"

rm "$BG" "$TMP"
