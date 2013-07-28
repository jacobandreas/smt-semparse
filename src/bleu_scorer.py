import os
import subprocess
import sys

class BLEUScorer:

  def __init__(self, config):
    self.config = config

  def run(self):
    args = [self.config.bleu_eval, '%s/test.nl' % self.config.experiment_dir]
    infile = open('%s/hyp.nl' % self.config.experiment_dir)
    nullfile = open(os.devnull, 'w')
    p = subprocess.Popen(args, stdin=infile, stdout=sys.stdout, stderr=nullfile)
    p.wait()
    infile.close()
    nullfile.close()
