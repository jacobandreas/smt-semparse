import cPickle

class Vocabulary:

  OOV_VAL = -1

  def __init__(self):
    self.str_to_tok = {}
    self.tok_to_str = {}

  def put(self, string):
    if string in self.str_to_tok:
      raise ValueError("%s is already in this vocabulary (token %d)" % \
          (string, self.str_to_tok[string]))
    return self.ensure(string)

  def ensure(self, string):
    if string in self.str_to_tok:
      return
    tok = len(self)
    self.str_to_tok[string] = tok
    self.tok_to_str[tok] = string
    return tok

  def gett(self, string):
    if string not in self.str_to_tok:
      return self.OOV_VAL
    return self.str_to_tok[string]

  def gets(self, tok):
    return self.tok_to_str[tok]

  def strs(self):
    return self.str_to_tok.keys()

  def toks(self):
    return self.tok_to_str.keys()

  def __len__(self):
    return len(self.str_to_tok)

  def save(self, path):
    with open(path, 'w') as f:
      cPickle.dump(self, f)

  @classmethod
  def load(cls, path):
    with open(path) as f:
      return cPickle.load(f)
