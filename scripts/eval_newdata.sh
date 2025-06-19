#!/bin/bash

sem_file=$1
results_dir="results"

datetime=`date '+%Y/%m/%d %H:%M:%S'`
echo $datetime > $results_dir/summary.txt
python scripts/eval_newdata.py $sem_file
python scripts/summary_newdata.py $results_dir
datetime=`date '+%Y/%m/%d %H:%M:%S'`
echo $datetime >> $results_dir/summary.txt
