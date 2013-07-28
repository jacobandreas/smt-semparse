import gzip
import re
from nlp_tools.hypergraph import Hypergraph
import itertools
import logging
from collections import defaultdict
import os

class Rule:

  MOSES_SYMBOL = '[X]'

  def __init__(self, rule_id, symbol, src, tgt, coindexing):
    self.rule_id = rule_id
    self.symbol = symbol
    self.src = src
    self.tgt = tgt
    self.coindexing = coindexing
    self.degree = len(self.coindexing)

  @classmethod
  def from_moses(cls, rule_id, rule_table_line):
    nl, mrl, scores, alignments, counts = re.split(r'\ ?\|\|\|\ ?',
        rule_table_line.strip())
    nl = nl.split()[:-1]
    nl = [cls.MOSES_SYMBOL if t == '[X][X]' else t for t in nl]
    mrl = mrl.split()[:-1]
    mrl = [cls.MOSES_SYMBOL if t == '[X][X]' else t for t in mrl]
    coindexing = []
    for pair in alignments.split():
      i_s, i_t = pair.split('-')
      coindexing.append((int(i_s), int(i_t)))
    return Rule(rule_id, cls.MOSES_SYMBOL, nl, mrl, coindexing)

  @classmethod
  def glue(cls, rule_id):
    return Rule(rule_id, cls.MOSES_SYMBOL, [cls.MOSES_SYMBOL, cls.MOSES_SYMBOL],
        [cls.MOSES_SYMBOL, cls.MOSES_SYMBOL], [(0,0), (1,1)])

  def __eq__(self, other):
    return other.__class__ == self.__class__ and self.rule_id == other.rule_id

  def __hash__(self):
    return self.rule_id

  def __repr__(self):
    return 'Rule<(%d) %s -> %s : %s>' % (self.rule_id, self.symbol, self.src,
        self.tgt)

class NLReweighter:

  def __init__(self, config):
    self.config = config

  def run(self):
    rules = self.load_rule_table()
    glue = Rule.glue(len(rules))
    all_counts = defaultdict(lambda: 0)
    successful_counts = defaultdict(lambda: 0)

    with open('%s/unlabeled.nl' % self.config.experiment_dir) as ul_f:
      for line in ul_f:
        toks = line.strip().split()
        chart = self.parse(toks, rules, glue)
        if not chart:
          continue
        self.collect_all_counts(all_counts, chart)
        self.collect_successful_counts(successful_counts, chart, toks)

    if not self.config.ul_only:
      with open('%s/train.nl' % self.config.experiment_dir) as t_f:
        for line in t_f:
          toks = line.strip().split()
          chart = self.parse(toks, rules, glue)
          # TODO is this an OOV issue?
          if not chart:
            continue
          self.collect_all_counts(all_counts, chart)
          self.collect_successful_counts(successful_counts, chart, toks)

    #self.write_updated_model(all_counts)
    self.write_updated_model(successful_counts)

  def load_rule_table(self):
    rule_table_path = '%s/model/rule-table.gz' % self.config.experiment_dir
    rules = {}
    with gzip.open(rule_table_path) as rule_table_f:
      for line in rule_table_f.readlines():
        rule = Rule.from_moses(len(rules), line)
        rules[rule.rule_id] = rule
    return rules

  def write_updated_model(self, counts):
    old_rule_table_path = '%s/model/rule-table.gz' % self.config.experiment_dir
    new_rule_table_path = '%s/model/rule-table-new.gz' % self.config.experiment_dir
    counter = 0
    with gzip.open(old_rule_table_path) as old_rule_table_f:
      with gzip.open(new_rule_table_path, 'w') as new_rule_table_f:
        for line in old_rule_table_f:
          nl, mrl, scores, alignments, rule_counts = re.split(r'\ ?\|\|\|\ ?',
              line.strip())
          scores = '%s %f' % (scores, counts[counter])
          newline = ' ||| '.join([nl, mrl, scores, alignments, rule_counts])
          newline = re.sub(r'\s+', ' ', newline)
          print >>new_rule_table_f, newline
          counter += 1

    old_config_path = '%s/model/moses.ini' % self.config.experiment_dir
    new_config_path = '%s/model/moses-new.ini' % self.config.experiment_dir
    with open(old_config_path) as old_config_f:
      with open(new_config_path, 'w') as new_config_f:
        for line in old_config_f:
          if line[-14:-1] == 'rule-table.gz':
            line = line[:6] + '6' + line[7:]
            #line[6] = '6'
          print >>new_config_f, line,
          if line == '[weight-t]\n':
            print >>new_config_f, '0.20'

    os.rename(new_rule_table_path, old_rule_table_path)
    os.rename(new_config_path, old_config_path)

  def parse(self, sent, grammar, glue):
    chart = dict()

    for span in range(1, len(sent)+1):
      for start in range(len(sent)+1-span):
        chart[start,span] = list()
        for rule in grammar.values():
          matches = self.match(sent, rule, start, span, chart)
          chart[start,span] += matches

    for i in range(1, len(sent)):
      if chart[0,i] and chart[i,len(sent)-i]:
        psets = [(c1, c2) for c1 in chart[0,i] for c2 in chart[i,len(sent)-i]]
        chart[0,len(sent)].append(Hypergraph(glue, psets))

    if not chart[0,len(sent)]:
      #logging.debug('failed to parse')
      return None
    else:
      #logging.debug('parse OK!')
      return chart

  def match(self, sent, rule, start, span, chart):

    if rule.degree == 0:
      if span != len(rule.src):
        return []
      if sent[start:start+span] != rule.src:
        return []
      return [Hypergraph(rule, [])]

    elif rule.degree == 1:
      nt_start = start + rule.coindexing[0][0]
      nt_span = span - len(rule.src) + 1
      if nt_span <= 0:
        return []
      if sent[start:nt_start] != rule.src[0:rule.coindexing[0][0]]:
        return []
      if sent[nt_start+nt_span:start+span] != rule.src[rule.coindexing[0][0]+1:]:
        return []

      pointer_sets = [i for i in chart[nt_start, nt_span] if i.label.symbol ==
          rule.src[rule.coindexing[0][0]]]
      ## if not chart[nt_start, nt_span]:
      ##   return []
      if not pointer_sets:
        return []
      return [Hypergraph(rule, [(i,) for i in pointer_sets])]

    elif rule.degree == 2:
      matches = []
      before_dist = rule.coindexing[0][0]
      between_dist = rule.coindexing[1][0] - rule.coindexing[0][0] - 1
      before_2_dist = rule.coindexing[1][0]
      nt_total_span = span - len(rule.src) + 2
      if nt_total_span <= 0:
        return []
      nt1_start = start + before_dist
      for nt1_span in range(1,nt_total_span):
        nt2_start = nt1_start + nt1_span + between_dist
        nt2_span = nt_total_span - nt1_span

        if sent[start:nt1_start] != rule.src[0:before_dist]:
          continue
        if sent[nt1_start+nt1_span:nt2_start] != rule.src[before_dist+1:before_2_dist]:
          continue
        if sent[nt2_start+nt2_span:start+span] != rule.src[before_2_dist+1:]:
          continue

        pointer_sets_1 = [i for i in chart[nt1_start,nt1_span] if i.label.symbol ==
            rule.src[rule.coindexing[0][0]]]
        pointer_sets_2 = [i for i in chart[nt2_start,nt2_span] if i.label.symbol ==
            rule.src[rule.coindexing[1][0]]]

        if not (pointer_sets_1 and pointer_sets_2):
          continue

        matches.append(Hypergraph(rule, list(itertools.product(pointer_sets_1,
          pointer_sets_2))))
        #matches.append(rule.rule_id)

      return matches

    assert False

  def collect_all_counts(self, counts, chart):
    for cell in chart.values():
      for node in cell:
        counts[node.label.rule_id] += 1

  def collect_successful_counts(self, counts, chart, sent):
    used = set()
    for cell in chart[0, len(sent)]:
      self.mark_used(used, cell)
    for cell in chart.values():
      for node in cell:
        if node in used:
          counts[node.label.rule_id] += 1

  def mark_used(self, used, cell):
    for edge in cell.edges:
      for ccell in edge:
        if ccell not in used:
          self.mark_used(used, ccell)
    used.add(cell)
