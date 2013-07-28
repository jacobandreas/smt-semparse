class QueryComparer:

  def __init__(self, config):
    self.config = config

  def run(self):

    hyp_file = open('%s/hyp.fun' % self.config.experiment_dir)
    ref_file = open('%s/test.fun' % self.config.experiment_dir)
    out_file = open('%s/eval.scored' % self.config.experiment_dir, 'w')

    hyps = {}
    for line in hyp_file:
      idx, hyp, scores1, scores2 = line.split(' ||| ')
      hyps[int(idx)] = hyp

    i = -1
    for line in ref_file:
      i += 1
      if i not in hyps:
        print >>out_file, 'empty'
        continue
      test = line.strip()
      if hyps[i] == test:
        print >>out_file, 'yes', 0
      else:
        print >>out_file, 'no', 0

    hyp_file.close()
    ref_file.close()
    out_file.close()
