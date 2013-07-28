#!/usr/bin/env python2

import sys
import subprocess
from nltk.stem.porter import PorterStemmer
from src.functionalizer import Functionalizer
import re
import os

def pretty_print_prolog(ans):
  ans = re.sub(r'\w+\(([^)]+)\)', r'\1', ans)
  parts = ans[1:-2].split(',')
  print '\n'.join(parts)
  #for part in parts:
  #  if 'stateid' in part:
  #    part = part[8:-1]
  #  print part

MOSES='/home/jacob/src/3p/mosesdecoder/dist/bin/moses_chart'
#WORK_DIR='/home/jacob/src/smt-semparse/work/DEMO'
WORK_DIR=os.path.realpath('latest')

fcr = Functionalizer(None)

moses_args = [MOSES, 
              '-drop-unknown',
              '-f', '%s/mert-work/moses.ini' % WORK_DIR]

moses = subprocess.Popen(moses_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

prolog_args = ['/usr/bin/swipl',
               '-l', '/home/jacob/src/3p/wasp-1.0/data/geo-funql/eval/eval.pl']

prolog = subprocess.Popen(prolog_args, stdin=subprocess.PIPE,
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

while True:

  print '\n\n? ',
  line = sys.stdin.readline()
  print
  print >>moses.stdin, line
  mrl = moses.stdout.readline().strip()
  moses.stdout.readline()

  fun = fcr.functionalize(mrl)
  print '!', fun

  plg = 'execute_funql_query(%s, A), print(A), nl.\n' % fun
  print >>prolog.stdin, plg
  answer = prolog.stdout.readline()
  print
  pretty_print_prolog(answer)
