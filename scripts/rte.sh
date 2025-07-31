#!/bin/bash
c2l_dir="ccg2lambda"
nbest=11 # more than 10 is recommended

tregex_dir=`cat scripts/tregex_location.txt`
export CLASSPATH=$tregex_dir/stanford-tregex.jar:$CLASSPATH

semantic_templates=$2
sentences_fname=$1
sentences_basename=`basename $1 | sed 's/\..*//'`

plain_dir="cache"
parsed_dir="cache"
results_dir="results"

mkdir -p $plain_dir $parsed_dir $results_dir
mkdir -p "tptp"

echo "pretokenizing $sentences_fname -> $parsed_dir/$sentences_basename.{tok, tag}"
python scripts/pretokenize.py $sentences_fname \
    --token-output $parsed_dir/$sentences_basename.tok \
    --tag-output $parsed_dir/$sentences_basename.tag

echo "depccg parsing $parsed_dir/$sentences_basename.tok -> $parsed_dir/$sentences_basename.init.jigg.xml"
depccg_ja \
    --input $parsed_dir/$sentences_basename.tok \
    --input-format raw \
    --nbest $nbest \
    --format jigg_xml \
    --pre-tokenized \
    > $parsed_dir/$sentences_basename.init.jigg.xml \
    2> $parsed_dir/$sentences_basename.log

python scripts/modify_tags.py \
    $parsed_dir/$sentences_basename.init.jigg.xml \
    $parsed_dir/$sentences_basename.tag

echo "selecting tree $parsed_dir/$sentences_basename.init.jigg.xml -> $parsed_dir/$sentences_basename.ptb"
python scripts/xml2ptb.py \
    $parsed_dir/$sentences_basename.init.jigg.xml \
    > $parsed_dir/$sentences_basename.mid.ptb

scripts/select_tree.sh \
    $parsed_dir/$sentences_basename.mid.ptb \
    $parsed_dir/$sentences_basename.ptb \
    $nbest

echo "executing tsurgeon $parsed_dir/$sentences_basename.ptb -> $parsed_dir/$sentences_basename.tsgn.ptb"
java -mx100m edu.stanford.nlp.trees.tregex.tsurgeon.Tsurgeon -s \
    -treeFile $parsed_dir/$sentences_basename$i.ptb scripts/transform.tsgn \
    > $parsed_dir/$sentences_basename.tsgn.ptb


echo "converting $parsed_dir/$sentences_basename.tsgn.ptb -> $parsed_dir/$sentences_basename.jigg.xml"
cat $parsed_dir/$sentences_basename.tsgn.ptb \
    | sed "s/</(/g" \
    | sed "s/>/)/g" \
    | sed "s/~/=/g" \
    | sed "s/\`/[/g" \
    | sed "s/'/]/g" \
    | sed "s/] ;/];/g" \
    | sed "s/) ;/);/g" \
    | sed "s/;\S*//g" \
    > $parsed_dir/$sentences_basename.tsgn.mod.ptb

python scripts/ptb2xml.py $parsed_dir/$sentences_basename.tsgn.mod.ptb \
    > $parsed_dir/$sentences_basename.jigg.xml

echo "semantic parsing $parsed_dir/$sentences_basename.jigg.xml -> $parsed_dir/$sentences_basename.sem.xml"
python $c2l_dir/semparse.py \
    $parsed_dir/$sentences_basename.jigg.xml \
    $semantic_templates \
    $parsed_dir/$sentences_basename.sem.xml \
    --arbi-types \
    2> $parsed_dir/$sentences_basename.sem.err

python $c2l_dir/visualize.py $parsed_dir/$sentences_basename.sem.xml \
    > $results_dir/$sentences_basename.html

echo "judging entailment $parsed_dir/$sentences_basename.sem.xml -> $results_dir/$sentences_basename.answer"
timeout 100 python scripts/eval.py \
    $parsed_dir/$sentences_basename.sem.xml \
    > $results_dir/$sentences_basename.answer \
    2> $results_dir/$sentences_basename.err
rte_answer=`cat $results_dir/$sentences_basename.answer`
echo $rte_answer