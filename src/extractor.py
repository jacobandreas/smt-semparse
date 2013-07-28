from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import GermanStemmer
import os
import re
import util
import xml.etree.ElementTree as ET

class IdStemmer:
  def stem(self, word):
    return word

class Extractor:

  NP_WEIGHT = 50

  def __init__(self, config):
    self.config = config
    if config.stem:
      if config.lang == 'en':
        self.stemmer = PorterStemmer()
      elif config.lang == 'de':
        self.stemmer = GermanStemmer()
      else:
        self.stemmer = IdStemmer()

  def run(self):
    if self.config.corpus == 'geo':
      self.run_geo()
    elif self.config.corpus == 'robo':
      self.run_robo()
    elif self.config.corpus == 'atis':
      self.run_atis()
    else:
      assert False

  def run_atis(self):

    train_nl = open('%s/train.nl' % self.config.experiment_dir, 'w')
    train_nl_lm = open('%s/train.nl.lm' % self.config.experiment_dir, 'w')
    train_nl_np = open('%s/train.np.nl' % self.config.experiment_dir, 'w')
    train_mrl = open('%s/train.mrl' % self.config.experiment_dir, 'w')
    train_mrl_lm = open('%s/train.mrl.lm' % self.config.experiment_dir, 'w')
    train_mrl_np = open('%s/train.np.mrl' % self.config.experiment_dir, 'w')
    train_fun = open('%s/train.fun' % self.config.experiment_dir, 'w')
    tune_nl = open('%s/tune.nl' % self.config.experiment_dir, 'w')
    tune_mrl = open('%s/tune.mrl' % self.config.experiment_dir, 'w')
    test_nl = open('%s/test.nl' % self.config.experiment_dir, 'w')
    test_mrl = open('%s/test.mrl' % self.config.experiment_dir, 'w')
    test_fun = open('%s/test.fun' % self.config.experiment_dir, 'w')
    
    if self.config.run == 'debug':
      with open('%s/atis-train.sem' % self.config.data_dir) as data_file:
        counter = 0
        for line in data_file:
          nl, slot = line.split('<=>', 1)
          nl = self.preprocess_nl(nl)
          slot = self.replace_specials(slot)
          fun = self.slot_to_fun(slot)
          mrl = util.fun_to_mrl(fun, True)
          if counter % 4 in (0,1):
            print >>train_nl, nl
            print >>train_mrl, mrl
            print >>train_fun, fun
            print >>train_nl_np, nl
            print >>train_mrl_np, mrl
            print >>train_nl_lm, '<s>', nl, '</s>'
            print >>train_mrl_lm, '<s>', mrl, '</s>'
          elif counter % 4 == 2:
            print >>tune_nl, nl
            print >>tune_mrl, mrl
          else:
            print >>test_nl, nl
            print >>test_mrl, mrl
            print >>test_fun, fun
          counter += 1

    else:
      train_path = '%s/atis-train.sem' % self.config.data_dir
      if self.config.run == 'dev':
        tune_path = train_path
        test_path = '%s/atis-dev.sem' % self.config.data_dir
      elif self.config.run == 'test':
        tune_path = '%s/atis-dev.sem' % self.config.data_dir
        test_path = '%s/atis-test.sem' % self.config.data_dir

      with open(train_path) as train_file:
        for line in train_file:
          nl, slot = line.split('<=>', 1)
          nl = self.preprocess_nl(nl)
          slot = self.replace_specials(slot)
          fun = self.slot_to_fun(slot)
          mrl = util.fun_to_mrl(fun, True)
          print >>train_nl, nl
          print >>train_mrl, mrl
          print >>train_fun, fun
          print >>train_nl_np, nl
          print >>train_mrl_np, mrl
          print >>train_nl_lm, '<s>', nl, '</s>'
          print >>train_mrl_lm, '<s>', mrl, '</s>'

      with open(tune_path) as tune_file:
        for line in tune_file:
          nl, slot = line.split('<=>', 1)
          nl = self.preprocess_nl(nl)
          slot = self.replace_specials(slot)
          fun = self.slot_to_fun(slot)
          mrl = util.fun_to_mrl(fun, True)
          print >>tune_nl, nl
          print >>tune_mrl, mrl

      with open(test_path) as test_file:
        for line in test_file:
          nl, slot = line.split('<=>', 1)
          nl = self.preprocess_nl(nl)
          slot = self.replace_specials(slot)
          fun = self.slot_to_fun(slot)
          mrl = util.fun_to_mrl(fun, True)
          print >>test_nl, nl
          print >>test_mrl, mrl
          print >>test_fun, fun

    for np_name in os.listdir('%s/db' % self.config.data_dir):
      np_path = '%s/db/%s' % (self.config.data_dir, np_name)
      with open(np_path) as np_file:
        for line in np_file:
          names = re.findall(r'"([^"]+)"', line)
          for name in names:
            nl = name
            mrl = "%s" % self.replace_specials(name)
            mrl = mrl.replace(' ', '_')
            mrl = mrl + '@s'
            print >>train_nl_np, nl
            print >>train_mrl_np, mrl
            print >>train_nl_lm, nl
            print >>train_mrl_lm, mrl

    train_nl.close()
    train_nl_lm.close()
    train_mrl.close()
    train_mrl_lm.close()
    train_fun.close()
    test_nl.close()
    test_mrl.close()
    test_fun.close()
    tune_nl.close()
    tune_mrl.close()

  def run_robo(self):

    train_ids, tune_ids, test_ids = self.get_folds()
    tune_ids = test_ids

    train_nl = open('%s/train.nl' % self.config.experiment_dir, 'w')
    train_nl_lm = open('%s/train.nl.lm' % self.config.experiment_dir, 'w')
    train_nl_np = open('%s/train.np.nl' % self.config.experiment_dir, 'w')
    train_mrl = open('%s/train.mrl' % self.config.experiment_dir, 'w')
    train_mrl_lm = open('%s/train.mrl.lm' % self.config.experiment_dir, 'w')
    train_mrl_np = open('%s/train.np.mrl' % self.config.experiment_dir, 'w')
    train_fun = open('%s/train.fun' % self.config.experiment_dir, 'w')
    tune_nl = open('%s/tune.nl' % self.config.experiment_dir, 'w')
    tune_mrl = open('%s/tune.mrl' % self.config.experiment_dir, 'w')
    test_nl = open('%s/test.nl' % self.config.experiment_dir, 'w')
    test_mrl = open('%s/test.mrl' % self.config.experiment_dir, 'w')
    test_fun = open('%s/test.fun' % self.config.experiment_dir, 'w')

    corpus = ET.parse('%s/corpus.xml' % self.config.data_dir)
    corpus_root = corpus.getroot()

    for node in corpus_root.findall('example'):
      nl = node.find("nl[@lang='%s']" % self.config.lang).text
      nl = self.preprocess_nl(nl)
      clang = node.find("mrl[@lang='robocup-clang']").text
      clang = self.replace_specials(clang)
      fun = self.clang_to_fun(clang)
      #print fun
      mrl = util.fun_to_mrl(fun)
      eid = int(node.attrib['id'])

      if eid in tune_ids:
        print >>tune_nl, nl
        print >>tune_mrl, mrl
      elif eid in train_ids:
        print >>train_nl, nl
        print >>train_mrl, mrl
        print >>train_fun, fun
        print >>train_nl_np, nl
        print >>train_mrl_np, mrl
        print >>train_nl_lm, '<s>', nl, '</s>'
        print >>train_mrl_lm, '<s>', mrl, '</s>'
      if eid in test_ids:
      #elif eid in test_ids:
        print >>test_nl, nl
        print >>test_mrl, mrl
        print >>test_fun, fun

    nps_file = open('%s/names' % self.config.data_dir)
    while True:
      line = nps_file.readline()
      if not line:
        break
      nl = nps_file.readline().strip()[3:]
      nl = self.preprocess_nl(nl)
      nps_file.readline()
      nps_file.readline()
      while True:
        line = nps_file.readline().strip()
        if line == '':
          break
        m = re.match('^\*n:(Num|Unum|Ident) -> \(\{ (\S+) \}\)$', line)
        mrl = m.group(2) + '@0'
        for i in range(self.NP_WEIGHT):
          print >>train_nl_np, nl
          print >>train_mrl_np, mrl
          print >>train_nl_lm, nl
          print >>train_mrl_lm, mrl

    train_nl.close()
    train_nl_lm.close()
    train_mrl.close()
    train_mrl_lm.close()
    train_fun.close()
    test_nl.close()
    test_mrl.close()
    test_fun.close()
    tune_nl.close()
    tune_mrl.close()

  def run_geo(self):
    train_ids, tune_ids, test_ids = self.get_folds()

    train_nl = open('%s/train.nl' % self.config.experiment_dir, 'w')
    train_nl_lm = open('%s/train.nl.lm' % self.config.experiment_dir, 'w')
    train_nl_np = open('%s/train.np.nl' % self.config.experiment_dir, 'w')
    train_mrl = open('%s/train.mrl' % self.config.experiment_dir, 'w')
    train_mrl_lm = open('%s/train.mrl.lm' % self.config.experiment_dir, 'w')
    train_mrl_np = open('%s/train.np.mrl' % self.config.experiment_dir, 'w')
    train_fun = open('%s/train.fun' % self.config.experiment_dir, 'w')
    unlabeled_nl = open('%s/unlabeled.nl' % self.config.experiment_dir, 'w')
    tune_nl = open('%s/tune.nl' % self.config.experiment_dir, 'w')
    tune_mrl = open('%s/tune.mrl' % self.config.experiment_dir, 'w')
    test_nl = open('%s/test.nl' % self.config.experiment_dir, 'w')
    test_mrl = open('%s/test.mrl' % self.config.experiment_dir, 'w')
    test_fun = open('%s/test.fun' % self.config.experiment_dir, 'w')

    corpus = ET.parse('%s/corpus-true.xml' % self.config.data_dir)
    corpus_root = corpus.getroot()

    counter = 0
    #stop_labeling = False
    for node in corpus_root.findall('example'):
      nl = node.find("nl[@lang='%s']" % self.config.lang).text
      nl = self.preprocess_nl(nl)
      fun = node.find("mrl[@lang='geo-funql']").text
      fun = self.preprocess_fun(fun)
      #fun = self.replace_specials(fun)
      mrl = util.fun_to_mrl(fun)
      eid = int(node.attrib['id'])

      unlabel_this = (counter >= 10 * self.config.lfrac)
      counter += 1
      counter %= 10

      if eid in tune_ids:
        print >>tune_nl, nl
        print >>tune_mrl, mrl
      elif eid in train_ids and not unlabel_this:
        print >>train_nl, nl
        print >>train_mrl, mrl
        print >>train_fun, fun
        print >>train_nl_np, nl
        print >>train_mrl_np, mrl
        print >>train_nl_lm, '<s>', nl, '</s>'
        print >>train_mrl_lm, '<s>', mrl, '</s>'
      elif eid in train_ids and unlabel_this:
        print >>unlabeled_nl, nl
      elif eid in test_ids:
        print >>test_nl, nl
        print >>test_mrl, mrl
        print >>test_fun, fun

    nplist = ET.parse('%s/nps-true.xml' % self.config.data_dir)
    nplist_root = nplist.getroot()
    for node in nplist_root.findall('example'):
      fun = node.find("mrl[@lang='geo-funql']").text
      fun = self.preprocess_fun(fun)
      #fun = self.replace_specials(fun)
      mrl = util.fun_to_mrl(fun)
      big_np = len(mrl.split()) > 1
      if (self.config.np_type == 'big' and not big_np) or \
          (self.config.np_type == 'small' and big_np):
        continue
      for nl_node in node.findall("nl[@lang='%s']" % self.config.lang):
        nl = nl_node.text
        nl = self.preprocess_nl(nl)
        for i in range(self.NP_WEIGHT):
          print >>train_nl_np, nl
          print >>train_mrl_np, mrl
          print >>train_nl_lm, nl
          print >>train_mrl_lm, mrl

    train_nl.close()
    train_nl_lm.close()
    train_mrl.close()
    train_mrl_lm.close()
    train_fun.close()
    test_nl.close()
    test_mrl.close()
    test_fun.close()
    tune_nl.close()
    tune_mrl.close()

  def get_folds(self):

    if self.config.corpus == 'geo':
      if self.config.run in ('debug', 'dev'):
        train_ids_file = '%s/folds600/fold-%d-train.ids' \
                             % (self.config.data_dir, self.config.fold)
        tune_ids_file = None
        test_ids_file = '%s/folds600/fold-%d-test.ids' \
                             % (self.config.data_dir, self.config.fold)
      elif self.config.run == 'test':
        train_ids_file = '%s/split880/fold-0-train.ids' % self.config.data_dir
        tune_ids_file = '%s/split880/fold-0-tune.ids' % self.config.data_dir
        test_ids_file = '%s/split880/fold-0-test.ids' % self.config.data_dir

    elif self.config.corpus == 'robo':
      if self.config.run in ('debug', 'dev'):
        train_ids_file = '%s/split-300/run-0/fold-%d/train-N270' \
                             % (self.config.data_dir, self.config.fold)
        tune_ids_file = None
        test_ids_file = '%s/split-300/run-0/fold-%d/test' \
                             % (self.config.data_dir, self.config.fold)
      else:
        assert False

    train_ids = set()
    tune_ids = set()
    test_ids = set()
    with open(train_ids_file) as fold_file:
      for line in fold_file.readlines():
        train_ids.add(int(line))
    if tune_ids_file:
      with open(tune_ids_file) as fold_file:
        for line in fold_file.readlines():
          tune_ids.add(int(line))
    with open(test_ids_file) as fold_file:
      for line in fold_file.readlines():
        test_ids.add(int(line))

    return train_ids, tune_ids, test_ids

  def preprocess_nl(self, nl):
    nl = nl.strip().lower()
    if self.config.stem and self.config.lang == 'de':
      # German stemmer can't handle UTF-8
      nl = nl.encode('ascii', 'ignore')
    else:
      nl = nl.encode('utf-8', 'ignore')
    if nl[-2:] == ' .' or nl[-2:] == ' ?':
      nl = nl[:-2]
    if self.config.stem:
      nl = ' '.join([self.stemmer.stem(tok) for tok in nl.split()])
    return nl

  def preprocess_fun(self, fun):
    return fun.strip()

  def replace_specials(self, mrl):
    mrl = mrl.replace('.', 'xxd')
    mrl = mrl.replace("'", 'xxq')
    mrl = mrl.replace('/', 'xxs')
    #mrl = re.sub(r"(' *[^'()]*)\'([^'()]* *')", r'\1_q_\2', mrl)
    #mrl = re.sub(r"(' *[^'()]*)\.([^'()]* *')", r'\1_dot_\2', mrl)
    #mrl = re.sub(r"(' *[^'()]*)\/([^'()]* *')", r'\1_slash_\2', mrl)
    return mrl

  def clang_to_fun(self, clang):
    clang = clang.strip()
    clang = re.sub(r'\s+', ' ', clang)
    clang = re.sub(r'\{([\d|X]+( [\d|X]+)*)\}', r'(set \1)', clang)
    clang = re.sub(r'\(([\w.-]+) ?', r'\1(', clang)
    clang = self.strip_bare_parens(clang)
    clang = clang.replace('()', '')
    clang = clang.replace(' ', ',')
    clang = clang.replace('"', '')

    clang = re.sub(r'definerule\([^,]+,[^,]+,', r'definerule(', clang)

    return clang

  def strip_bare_parens(self, clang):
    try:
      start = clang.index(' (')+1
    except ValueError:
      return clang

    end = start+1
    pcounter = 0
    while pcounter >= 0:
      c = clang[end:end+1]
      if c == '(':
        pcounter += 1
      elif c == ')':
        pcounter -= 1
      end += 1
    end -= 1
    
    r = clang[:start] + clang[start+1:end] + clang[end+1:]
    return r

  def slot_to_fun(self, slot):
    slot = slot.strip()
    slot = slot.replace('value', '"value"')
    slot = slot.replace('="', "('")
    slot = slot.replace('",', "'),")
    slot = slot.replace('")', "'))")
    slot = slot.replace("'value'", 'value')
    return slot
