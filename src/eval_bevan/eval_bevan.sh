#!/bin/sh

in=$1
cat $in | sed 's/W//g' | sed 's/( /(/g' | sed 's/ )/)/g' | sed 's/#.*//g' | sed 's/^0$/0/' | sed 's/()//g' | sed 's/  /,/g' > clean
./format_prolog.py clean ~/src/semparse-old/work_psmt/test.fun > test.pl

swipl -l "/home/jacob/src/3p/wasp-1.0/data/geo-funql/eval/eval.pl" \
  < test.pl \
  > test.out
  2>> errlog
