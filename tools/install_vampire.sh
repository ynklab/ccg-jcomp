#!/bin/bash

vampire_url="https://github.com/vprover/vampire/archive/refs/tags/v4.9casc2024.tar.gz"
vampire_basename=`basename $vampire_url`
vampire_dirname="vampire-4.9casc2024"

if [ ! -d $vampire_dirname ]; then
    curl -LO $vampire_url
    tar -zxvf $vampire_basename
fi

vampire_dir=`pwd`"/"$vampire_dirname
echo $vampire_dir > scripts/vampire_location.txt

rm -f $vampire_basename

cd $vampire_dir
make vampire_rel
cp vampire_rel_* vampire