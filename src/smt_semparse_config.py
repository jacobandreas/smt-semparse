from config import Config

class SMTSemparseConfig(Config):

  def __init__(self, settings_path, dependencies_path):
    Config.__init__(self, settings_path, dependencies_path)

    self.put('data_dir', '%s/data/%s' % (self.smt_semparse, self.corpus))

    if self.np:
      self.train_name = 'train.np'
    else:
      self.train_name = 'train'

    self.put('srilm_ngram_count', '%s/bin/%s/ngram-count' % \
                                 (self.srilm, self.srilm_arch))

    self.put('moses_train', '%s/scripts/training/train-model.perl' % self.moses)
    self.put('moses_tune', '%s/scripts/training/mert-moses.pl' % self.moses)
    self.put('moses_decode_phrase', '%s/dist/bin/moses' % self.moses)
    self.put('moses_decode_hier', '%s/dist/bin/moses_chart' % self.moses)
    self.put('bleu_eval', '%s/scripts/generic/multi-bleu.perl' % self.moses)

    self.put('wasp_eval', '%s/data/geo-funql/eval/eval.pl' % self.wasp)

    if self.nlg:
      self.put('src', 'mrl')
      self.put('tgt', 'nl')
    else:
      self.put('src', 'nl')
      self.put('tgt', 'mrl')
