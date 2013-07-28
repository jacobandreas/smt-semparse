import subprocess

class GeoWorld:

  def __init__(self, config):
    self.config = config

  def run(self):
    self.write_queries()

    infile = open('%s/eval.pl' % self.config.experiment_dir)
    log = open('%s/prolog.log' % self.config.experiment_dir, 'w')
    outfile = open('%s/eval.out' % self.config.experiment_dir, 'w')
    p = subprocess.Popen([self.config.prolog,
                          '-l', self.config.wasp_eval],
                         stdin=infile,
                         stdout=outfile,
                         stderr=log)
    p.wait()
    infile.close()
    log.close()
    outfile.close()

    self.extract_results()

  def write_queries(self):

    hyp_file = open('%s/hyp.fun' % self.config.experiment_dir)
    ref_file = open('%s/test.fun' % self.config.experiment_dir)
    query_file = open('%s/eval.pl' % self.config.experiment_dir, 'w')

    examples = []
    hyp_list = []
    last_idx = 0
    for hyp_line in hyp_file.readlines():
      idx, hyp, scoreparts, score = hyp_line.split('|||')
      idx = int(idx)
      hyp = hyp.strip()
      if idx != last_idx:
        examples.append(hyp_list)
        for i in range(last_idx, idx-1):
          examples.append([])
        hyp_list = []
        last_idx = idx
      hyp_list.append((hyp,float(score)))
    examples.append(hyp_list)

    i = 0
    for ref, hyp_list in zip(ref_file.readlines(), examples):
      ref = ref.strip()
      for hyp, score in hyp_list:
        print >>query_file, \
          'catch(call_with_time_limit(1,eval([%d,%f,%s,%s])),E,writeln(\'error\')).\n' \
          % (i, score, ref, hyp)
      i += 1

    hyp_file.close()
    ref_file.close()
    query_file.close()

  def extract_results(self):

    eval_file = open('%s/eval.out' % self.config.experiment_dir)
    result_file = open('%s/eval.scored' % self.config.experiment_dir, 'w')

    examples = []
    hyp_list = []
    last_idx = 0
    for line in eval_file.readlines():
      if line == 'error\n':
        continue
      idx, score, result = line.split()
      idx = int(idx)
      score = float(score)
      if idx > last_idx:
        examples.append(hyp_list)
        last_idx += 1
        while idx > last_idx:
          examples.append([])
          last_idx += 1
        hyp_list = []
      hyp_list.append((result,score))
    examples.append(hyp_list)
    last_idx += 1

    if self.config.corpus == 'geo' and self.config.run in ('debug', 'dev'):
      top = 60
    elif self.config.corpus == 'geo' and self.config.run == 'test':
      top = 280
    else:
      assert False
    while top > last_idx:
      examples.append([])
      last_idx += 1

    for hyp_list in examples:
      if len(hyp_list) == 0:
        print >>result_file, 'empty'
        continue

      choice, score = hyp_list[0]
      if choice == 'y':
        print >>result_file, 'yes', score
      else:
        print >>result_file, 'no', score

    eval_file.close()
    result_file.close()
