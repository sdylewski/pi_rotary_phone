#!/bin/bash
#
# reformat all .wav files to be 22050 kHz, unsigned 16bit, mono
# for use in telephone
#
# need to install sox and libsox-fmt-mp3 (for mp3s)

if [ ! -d converted_files ] ; then
        echo "making directory converted_files"
        mkdir "converted_files"
fi

#for thisfile in *.wav ; do
#        filename=$( basename "$thisfile" '.wav' )
#        echo "filename=$filename"
#        soxi "$thisfile"
#        outfile="converted_files/$filename.wav"
#        sox "$thisfile" -c 1 -r 22050 -b 16 -e signed-integer "$outfile"
#        soxi "$outfile"
#done
#for thisfile in *.WAV ; do
#        filename=$( basename "$thisfile" '.WAV' )
#        echo "filename=$filename"
#        soxi "$thisfile"
#        filename=$(echo $filename | tr '[:upper:]' '[:lower:]')
#        echo "filename=$filename"
#        outfile="converted_files/$filename.wav"
#        echo "outfile=$outfile"
#        sox "$thisfile" -c 1 -r 22050 -b 16 -e signed-integer "$outfile"
#        soxi "$outfile"
#done

for thisfile in "$@" ; do
        filename=$(basename -- "$thisfile")
        extension="${filename##*.}"
        filename="${filename%.*}"
#        filename=$( basename "$thisfile" '.mp3' )
#        echo "filename=$filename"
#        soxi "$thisfile"
        filename_lower=$(echo $filename | tr '[:upper:]' '[:lower:]')
        outfile="converted_files/$filename_lower.wav"
#        if [ "$thisfile" != "$outfile" ] ; then
#            echo "moving $thisfile to originals/$filename.$extension"
#            mv "$thisfile" "originals/$filename.$extension"
#        fi 
        echo "$thisfile --> $outfile"
        sox "$thisfile" -c 1 -r 44100 -b 16 -e signed-integer "$outfile"
        soxi "$outfile"
done
