#!/bin/bash

TARGETDIR=$1

cd $TARGETDIR;

for folder in `ls -d -- */`
do 
    cd $folder ;
    mogrify -format tiff *png
    rm *.png
    cd ..
done
