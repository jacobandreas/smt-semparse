import logging
import os
from extractor import Extractor
from functionalizer import Functionalizer
from slot_checker import SlotChecker
from srilm import SRILM
from moses import Moses
from nl_reweighter import NLReweighter
from geo_world import GeoWorld
from query_comparer import QueryComparer
from bleu_scorer import BLEUScorer

class SMTSemparseExperiment:

  def __init__(self, config):
    self.config = config

  def run_fold(self, fold):
    logging.info('running fold %d', fold)
    self.config.put('fold', fold)
    fold_dir = os.path.join(self.config.work_dir, str(fold))
    self.config.put('experiment_dir', fold_dir)
    os.makedirs(fold_dir)
    self.run()

  def run_split(self):
    logging.info('running split')
    self.config.put('experiment_dir', self.config.work_dir)
    self.run()

  def run(self):
    logging.info('working dir is %s', self.config.experiment_dir)

    # get data
    logging.info('extracting data')
    Extractor(self.config).run()

    # learn lm
    logging.info('learning LM')
    SRILM(self.config).run_ngram_count()

    # train moses
    moses = Moses(self.config)
    logging.info('training TM')
    moses.run_train()

    # reweight using monolingual data
    if self.config.monolingual:
      logging.info('learning from monolingual data')
      NLReweighter(self.config).run()

    # filter disconnected rules
    if self.config.filter:
      logging.info('filtering disconnected rules')
      moses.filter_phrase_table()

    # tune moses
    if self.config.run == 'test':
      logging.info('tuning TM')
      moses.run_tune()

    if self.config.retrain:
      logging.info('retraining TM')
      moses.run_retrain()

    # decode input
    logging.info('decoding')
    moses.run_decode()

    if self.config.nlg:
      logging.info('running BLEU')
      BLEUScorer(self.config).run()
      pass

    else:
      # functionalize
      logging.info('functionalizing')
      Functionalizer(self.config).run()

      # compare answers
      logging.info('executing queries')
      if self.config.corpus == 'geo':
        GeoWorld(self.config).run()
      elif self.config.corpus == 'atis':
        SlotChecker(self.config).run()
      else:
        QueryComparer(self.config).run()
