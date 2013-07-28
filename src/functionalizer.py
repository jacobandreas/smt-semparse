import logging
import util
import sys

class Functionalizer:

  def __init__(self, config):
    self.config = config

  def run(self):
    hyp_file = open('%s/hyp.mrl.nbest' % self.config.experiment_dir)
    fun_file = open('%s/hyp.fun' % self.config.experiment_dir, 'w')

    hypsets = []
    hypset = []
    last_eid = 0
    for line in hyp_file:
      parts = line.split('|||')
      eid = int(parts[0])
      if eid != last_eid:
        hypsets.append(hypset)
        hypset = []
        last_eid = eid
      score = parts[2] + ' ||| ' + parts[3].strip()
      hyp = parts[1].strip()
      hypset.append((hyp,score))
    hypsets.append(hypset)

    counter = 0
    for hypset in hypsets:
      hypset = list(reversed(hypset))
      while hypset:
        hyp, score = hypset.pop()
        fun = self.functionalize(hyp)
        if fun:
          print >>fun_file, counter, '|||', fun, '|||', score
          break
      counter += 1

  #xc = 0
  def functionalize(self, mrl):

    #if '_@0' in mrl and 'cityid@2' in mrl:
    #  #print '==='
    #  #print mrl
    #  self.xc += 1
    #  if self.xc > 5:
    #    exit()

    stack = []
    r = []
    tokens = list(reversed(mrl.split()))

    #print tokens

    while tokens:
      it = tokens.pop()
      #print it
      if util.ARITY_SEP not in it:
        token = it
        arity = util.ARITY_STR
        logging.warn('unrecognized token: %s', it)
      else:
        token, arity = it.rsplit(util.ARITY_SEP)
      if arity == util.ARITY_STR:
        arity = 0
        arity_str = True
      elif not (arity == util.ARITY_ANY):
        arity = int(arity)
        arity_str = False
      
      if arity == util.ARITY_ANY or arity > 0:
        r.append(token)
        r.append('(')
        stack.append(arity)
      else:
        assert arity == 0
        if arity_str:
          r.append("'%s'" % token.replace('_', ' '))
        else:
          r.append(token)
          #print r
        while stack:
          top = stack.pop()
          if top == util.ARITY_ANY and tokens:
            r.append(',')
            stack.append(util.ARITY_ANY)
            break
          elif top != util.ARITY_ANY and top > 1:
            r.append(',')
            stack.append(top - 1)
            break
          else:
            r.append(')')

        if not stack and tokens:
          return None

    if stack:
      return None

    r = ''.join(r)

    # nasty hacks to fix misplaced _
    if '(_' in r:
      return None
    if ',_' in r and not ('cityid' in r):
      return None
    if '_),_)' in r:
      return None

    return r
