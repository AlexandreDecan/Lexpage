#!/bin/bash
# Usage: $0 color directory
# Example: ./gen-font.sh ffcc00 lexpage

mkdir -p $2

for i in black/*.svg
do
    sed "s@<path @<path style=\"fill:#$1;fill-opacity:0.1\" @g" $i > $2/$(basename $i)
done
