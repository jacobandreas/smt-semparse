class Evaluator:

  def __init__(self, config):
    self.config = config

  def run(self):
    if self.config.run == 'debug':
      s_p, s_r, s_f = self.score('%s/1' % self.config.work_dir)
    elif self.config.run == 'dev':
      s_p = 0
      s_r = 0
      s_f = 0
      for i in range(10):
        p, r, f = self.score('%s/%d' % (self.config.work_dir, i))
        s_p += p
        s_r += r
        s_f += f
      s_p /= 10
      s_r /= 10
      s_f /= 10
    elif self.config.run == 'test':
      s_p, s_r, s_f = self.score(self.config.work_dir)

    print 'p: %f\nr: %f\nf: %f' % (s_p, s_r, s_f)

  def score(self, experiment_dir):
    result_file = open('%s/eval.scored' % (experiment_dir))
    tp = 0
    fp = 0
    count = 0
    for line in result_file.readlines():
      count += 1
      tag = line.strip()
      if tag == 'empty':
        continue
      tag, score = tag.split()
      score = float(score)
      if tag == 'yes':
        tp += 1
      elif tag == 'no':
        fp += 1

    p = 1.0 * tp / (tp + fp)
    r = 1.0 * tp / count
    f = 2.0 * p * r / (p + r)

    return (p, r, f)
