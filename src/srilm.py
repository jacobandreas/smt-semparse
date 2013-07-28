import logging
import subprocess

class SRILM:

  def __init__(self, config):
    self.config = config

  def run_ngram_count(self):
    log = open('%s/lm.log' % self.config.experiment_dir, 'w')
    p = subprocess.Popen([self.config.srilm_ngram_count,
                          '-text', '%s/train.%s.lm' % (self.config.experiment_dir, self.config.tgt),
                          '-order', '3',
                          '-no-sos',
                          '-no-eos',
                          '-lm', '%s/%s.arpa' % (self.config.experiment_dir, self.config.tgt),
                          '-unk'],
                          stderr=log)
    p.wait()
    log.close()
