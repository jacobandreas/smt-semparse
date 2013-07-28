#!/usr/bin/env python2

import os
import datetime
import logging
from src.evaluator import Evaluator
from src.smt_semparse_config import SMTSemparseConfig
from src.smt_semparse_experiment import SMTSemparseExperiment

LOGFILE_NAME = 'run.log'

def run_one(config):
  # create work dir for this run
  # moses can't handle paths with colons
  timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H.%M.%S')
  run_work_dir = os.path.join(base_work_dir, timestamp)
  assert not os.path.exists(run_work_dir)
  os.makedirs(run_work_dir)
  config.put('work_dir', run_work_dir)
  if os.path.exists('latest'):
    os.remove('latest')
  os.symlink(run_work_dir, 'latest')

  # set up logging
  if config.run == 'debug':
    logging.basicConfig(level=logging.DEBUG)
  else:
    log_path = os.path.join(run_work_dir, LOGFILE_NAME)
    logging.basicConfig(filename=log_path, level=logging.INFO)

  experiment = SMTSemparseExperiment(config)
  if config.run == 'debug':
    experiment.run_fold(1)
  elif config.run == 'dev':
    for i in range(10):
      experiment.run_fold(i)
  elif config.run == 'test':
    experiment.run_split()
  else:
    assert False

  if not config.nlg:
    logging.info('evaluating')
    Evaluator(config).run()

if __name__ == '__main__':

  # load config
  config = SMTSemparseConfig('settings.yaml', 'dependencies.yaml')

  # create base work dir if it doesn't exist
  base_work_dir = os.path.join(config.smt_semparse, config.workdir)
  if not os.path.exists(base_work_dir):
    os.makedirs(base_work_dir)

  run_one(config)

  #for np in (True, False):
  #  for model in ('phrase', 'hier'):
  #    for lang in ('en', 'de', 'el', 'th'):
  #      print 'np: %s\nmodel: %s\nlang: %s' % (np, model, lang)
  #      config.put('np', np)
  #      config.put('model', model)
  #      config.put('lang', lang)
  #      if lang == 'en':
  #        config.put('symm', 'srctotgt')
  #      else:
  #        config.put('symm', 'tgttosrc')
  #      for i in range(10):
  #        run_one(config)

  #for lfrac in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
  ##for lfrac in (0.1,):
  #  for monolingual in (True, False):
  #  #for monolingual in (True,):
  #    for ul_only in (True, False):
  #    #for ul_only in (True,):
  #      if (not monolingual) and ul_only:
  #        continue
  #      config.put('lfrac', lfrac)
  #      config.put('monolingual', monolingual)
  #      config.put('ul_only', ul_only)
  #      print 'lfrac: %f' % lfrac
  #      print 'monolingual: %s' % monolingual
  #      print 'ul_only: %s' % ul_only
  #      for i in range(10):
  #      #for i in range(2):
  #        run_one(config)

