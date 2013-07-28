#!/usr/bin/env python2

import sys

while True:
  lfrac = sys.stdin.readline()
  if not lfrac:
    break
  monolingual = sys.stdin.readline()
  ul_only = sys.stdin.readline()

  print lfrac, monolingual, ul_only,

  p = 0
  r = 0
  f = 0

  for i in range(10):
    lp = float(sys.stdin.readline().split()[1])
    lr = float(sys.stdin.readline().split()[1])
    lf = float(sys.stdin.readline().split()[1])

    p += lp
    r += lr
    f += lf

  p /= 10
  r /= 10
  f /= 10

  print 'p:', p
  print 'r:', r
  print 'f:', f
