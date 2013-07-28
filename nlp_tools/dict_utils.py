"""
Utilities for doing math on sparse vectors indexed by arbitrary objects.
(These will usually be feature vectors.)
"""

import math_utils as mu
import math

def d_elt_op_keep(op, zero, args):
  """
  Applies op to arguments elementwise, keeping entries that don't occur in
  every argument (i.e. behaves like a sum).
  """
  ret = {}
  for d in args:
    for key in d:
      if key not in ret:
        ret[key] = d[key]
      else:
        ret[key] = op([ret[key], d[key]])
  for key in ret.keys():
    if ret[key] == zero:
      del ret[key]
  return ret

def d_elt_op_drop(op, args):
  """
  Applies op to arguments elementwise, discarding entries that don't occur in
  every argument (i.e. behaves like a product).
  """
  # avoid querying lots of nonexistent keys
  smallest = min(args, key=len)
  sindex = args.index(smallest)
  ret = dict(smallest)
  for i in range(len(args)):
    if i == sindex:
      continue
    d = args[i]
    for key in ret.keys():
      if key in d:
        ret[key] = op([ret[key], d[key]])
      else:
        del ret[key]
  return ret

def d_sum(args):
  """
  Computes a sum of vectors.
  """
  return d_elt_op_keep(sum, 0, args)

def d_logspace_sum(args):
  """
  Computes a sum of vectors whose elements are represented in logspace.
  """
  return d_elt_op_keep(mu.logspace_sum, -float('inf'), args)

def d_elt_prod(args):
  """
  Computes an elementwise product of vectors.
  """
  return d_elt_op_drop(lambda l: reduce(lambda a,b: a*b, l), args)

def d_dot_prod(d1, d2):
  """
  Takes the dot product of the two arguments.
  """
  # avoid querying lots of nonexistent keys
  if len(d2) < len(d1):
    d1, d2 = d2, d1
  dot_prod = 0
  for key in d1:
    if key in d2:
      dot_prod += d1[key] * d2[key]
  return dot_prod

def d_logspace_scalar_prod(c, d):
  """
  Multiplies every element of d by c, where c and d are both represented in
  logspace.
  """
  ret = {}
  for key in d:
    ret[key] = c + d[key]
  return ret

def d_op(op, d):
  """
  Applies op to every element of the dictionary.
  """
  ret = {}
  for key in d:
    ret[key] = op(d[key])
  return ret

# convenience methods
def d_log(d):
  return d_op(math.log, d)

def d_exp(d):
  return d_op(math.exp, d)
