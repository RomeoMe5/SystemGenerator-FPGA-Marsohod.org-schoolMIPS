#!/bin/bash
for dir in `ls -d */`; do
    cd $dir
    for file in `find . | grep -vE "(.(vwf|bdf|qpf)|^(.|..)$)"`; do
        rm -r $file
    done
    cd ..
done
