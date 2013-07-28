#!/usr/bin/env python2

import sys

def main():
  HYP_PATH = sys.argv[1]
  REF_PATH = sys.argv[2]

  hyp_file = open(HYP_PATH)
  ref_file = open(REF_PATH)

  hyps = []
  for hyp_line in hyp_file.readlines():
    hyp = hyp_line.strip()
    hyps.append(hyp)

  refs = []
  for r_line in ref_file.readlines():
    ref = r_line.strip()
    refs.append(ref)

  i = 0
  for ref, hyp in zip(refs, hyps):
    print \
      'catch(call_with_time_limit(1,eval([%d,%f,%s,%s])),E,writeln(\'error\')).\n' \
      % (i, 0, ref, hyp)
    i += 1

if __name__ == '__main__':
  main()
