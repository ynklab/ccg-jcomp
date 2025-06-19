#!/bin/bash

tregex_basename=stanford-tregex-4.2.0

wget https://nlp.stanford.edu/software/stanford-tregex-4.2.0.zip
unzip $tregex_basename.zip
echo `pwd`"/"$tregex_basename > scripts/tregex_location.txt

rm -f $tregex_basename.zip