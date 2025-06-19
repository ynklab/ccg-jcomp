#!/bin/bash

jsem_dir="jsem_plain"
output_file_name="main_result.html"
result_dir="results"
output_file=$result_dir/$output_file_name
semantic_templates=$1
num_problem=0
num_correct=0
red_color="rgb(255,0,0)"
green_color="rgb(0,255,0)"

for problem in `ls $jsem_dir/*.txt`
do
    problem_basename=`basename $problem | sed 's/\..*//'`
    ((num_problem++))
    scripts/rte_v2.sh $problem $semantic_templates
    gold_answer=`cat $jsem_dir/$problem_basename.answer`
    system_answer=`cat $result_dir/$problem_basename.answer`
    echo "system answer is "$system_answer
    echo "gold answer is "$gold_answer
    if [ "$gold_answer" == "$system_answer" ]; then
        ((num_correct++))
    fi
done


date=`date "+%Y/%m/%d %H:%M:%S"`
accuracy=`echo "scale=3; $num_correct/$num_problem" | bc`

echo \
"<!doctype html>
<html lang='ja'>
<head>
  <meta charset='UTF-8'>
  <title>Evaluation results of JSeM </title>
  <style>
    body {
      font-size: 1.5em;
    }
    #table {
        margin: auto;
    }
    td {
        padding: 5px;
    }
  </style>
</head>
<body>
<ul>
    <li>$date</li>
    <li>Accuracy: $accuracy</li>
</ul>
<table id=\"table\" border=\"1\">
<tr>
    <th colspan=\"3\"> problem </th>
    <th> gold answer </th>
    <th> system answer </th>
</tr>" \
    > $output_file

for problem in `ls $jsem_dir/*.txt`
do
    problem_basename=`basename $problem | sed 's/\..*//'`
    gold_answer=`cat $jsem_dir/$problem_basename.answer`
    system_answer=`cat $result_dir/$problem_basename.answer`
    num_sentence=`cat $problem | wc -l`
    i=0
    if [ "$gold_answer" == "$system_answer" ]; then
        color=$green_color
    else
        color=$red_color
    fi
    while read line
    do
        if [ $i -eq 0 ]; then
            echo -e \
            "<tr>\n" \
                "\t<td rowspan=\"$num_sentence\">$problem_basename</td>\n" \
                "\t<td>premise 1</td>\n" \
                "\t<td>$line</td>\n" \
                "\t<td style=\"text-align: center;\" rowspan=\"$num_sentence\">$gold_answer</td>\n" \
                "\t<td style=\"text-align: center;\" rowspan=\"$num_sentence\"><a style=\"background-color:$color\" href=\"$problem_basename.html\">$system_answer</a></td>\n" \
            "\t</tr>" \
                >> $output_file
        elif [ $i -lt $((num_sentence - 1)) ];then
            echo -e \
            "<tr>\n" \
                "\t<td>premise $((i + 1))</td>\n" \
                "\t<td>$line</td>\n" \
            "\t</tr>" \
                >> $output_file
        else
            echo -e \
            "<tr>\n" \
                "\t<td>hypothesis</td>\n" \
                "\t<td>$line</td>\n" \
            "\t</tr>" \
                >> $output_file
        fi
        ((i++))
    done < $problem
done


echo \
"</table>
</body>
</html>" \
    >> $output_file