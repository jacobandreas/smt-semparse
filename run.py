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
