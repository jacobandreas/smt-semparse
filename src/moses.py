import logging
import os
import subprocess
import gzip

class Moses:

  def __init__(self, config):
    self.config = config

  def run_train(self):
    args = [self.config.moses_train,
            '--root-dir', self.config.experiment_dir,
            '--corpus', '%s/%s' % (self.config.experiment_dir,
                                   self.config.train_name),
            '--f', self.config.src,
            '--e', self.config.tgt,
            '--lm', '0:3:%s/%s.arpa' % (self.config.experiment_dir, self.config.tgt),
            #'-score-options', "'--OnlyDirect --NoPhraseCount'"
            '--alignment', self.config.symm]
    if self.config.model == 'hier':
      args += ['-hierarchical', '-glue-grammar']

    logging.info(' '.join(args))

    log = open('%s/train.log' % self.config.experiment_dir, 'w')
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=log)
    p.wait()
    log.close()

  def run_retrain(self):
    old_train_nl = '%s/%s.nl' % (self.config.experiment_dir,
        self.config.train_name)
    old_train_mrl = '%s/%s.mrl' % (self.config.experiment_dir,
        self.config.train_name)
    moved_train_nl = '%s.notune' % old_train_nl
    moved_train_mrl = '%s.notune' % old_train_mrl
    tune_nl = '%s/tune.nl' % self.config.experiment_dir
    tune_mrl = '%s/tune.mrl' % self.config.experiment_dir
    os.rename(old_train_nl, moved_train_nl)
    os.rename(old_train_mrl, moved_train_mrl)
    with open(old_train_nl, 'w') as rt_train_nl:
      subprocess.call(['cat', moved_train_nl, tune_nl], stdout=rt_train_nl)
    with open(old_train_mrl, 'w') as rt_train_mrl:
      subprocess.call(['cat', moved_train_mrl, tune_mrl], stdout=rt_train_mrl)

    os.remove('%s/model/extract.inv.gz' % self.config.experiment_dir)
    os.remove('%s/model/extract.gz' % self.config.experiment_dir)
    if self.config.model == 'hier':
      os.remove('%s/model/rule-table.gz' % self.config.experiment_dir)
    else:
      os.remove('%s/model/phrase-table.gz' % self.config.experiment_dir)

    self.run_train()

  def parens_ok(self, line):
    mrl_part = line.split(' ||| ')[1]
    tokens = [t[-1] for t in mrl_part.split() if t[-2] == '@']
    tokens.reverse()
    stack = []
    while tokens:
      t = tokens.pop()
      assert t != '*'
      if t == 's':
        t = 0
      t = int(t)
      if t > 0:
        stack.append(t)
      else:
        while stack:
          top = stack.pop()
          if top > 1:
            stack.append(top - 1)
            break
        if tokens and not stack:
          return False
    return True

  def filter_phrase_table(self):
    table_name = 'phrase' if self.config.model == 'phrase' else 'rule'
    oldname = '%s/model/%s-table.gz' % (self.config.experiment_dir, table_name)
    newname = '%s/model/%s-table.old.gz' % (self.config.experiment_dir, table_name)
    os.rename(oldname, newname)

    with gzip.open(oldname, 'w') as filtered_table_f:
      with gzip.open(newname, 'r') as old_table_f:
        for line in old_table_f:
          if self.parens_ok(line):
            print >>filtered_table_f, line,

  def run_tune(self):
    wd = os.getcwd()
    os.chdir(self.config.experiment_dir)
    args = [self.config.moses_tune,
            '%s/tune.%s' % (self.config.experiment_dir, self.config.src),
            '%s/tune.%s' % (self.config.experiment_dir, self.config.tgt)]
    if self.config.model == 'hier':
      args += [self.config.moses_decode_hier]
    else:
      args += [self.config.moses_decode_phrase]
    args += ['%s/model/moses.ini' % self.config.experiment_dir,
             '--mertdir', '%s/dist/bin' % self.config.moses]
    if self.config.model == 'hier':
      args += ['--filtercmd', 
               '%s/scripts/training/filter-model-given-input.pl --Hierarchical'\
                   % self.config.moses]

    log = open('%s/tune.log' % self.config.experiment_dir, 'w')
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=log)
    p.wait()
    log.close()
    os.chdir(wd)

  def run_decode(self):
    if self.config.model == 'phrase':
      args = [self.config.moses_decode_phrase]
    elif self.config.model == 'hier':
      args = [self.config.moses_decode_hier]
    else:
      assert False

    if self.config.run == 'test':
      args += ['-f', '%s/mert-work/moses.ini' % self.config.experiment_dir]
    else:
      args += ['-f', '%s/model/moses.ini' % self.config.experiment_dir]
    #args += ['-f', '%s/model/moses.ini' % self.config.experiment_dir]

    args += ['-drop-unknown',
             '-n-best-list', '%s/hyp.%s.nbest' % (self.config.experiment_dir, self.config.tgt),
                             str(self.config.nbest), 'distinct',
             '-threads', '3']

    #nullfile = open(os.devnull, 'w')
    infile = open('%s/test.%s' % (self.config.experiment_dir, self.config.src))
    outfile = open('%s/hyp.%s' % (self.config.experiment_dir, self.config.tgt), 'w')
    log = open('%s/decode.log' % self.config.experiment_dir, 'w')
    p = subprocess.Popen(args, stdin=infile, stdout=outfile, stderr=log)
    p.wait()
    infile.close()
    log.close()
    outfile.close()
