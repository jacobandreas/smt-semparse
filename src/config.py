import yaml
import logging

class Config:

  def __init__(self, settings_path, dependencies_path):
    with open(settings_path) as settings_file:
      settings = yaml.load(settings_file)
    with open(dependencies_path) as dependencies_file:
      dependencies = yaml.load(dependencies_file)

    self.entries = {}

    for config in (settings, dependencies):
      for key, value in config.items():
        self.put(key, value)

  def __hasattr__(self, key):
    return key in self.entries

  def __getattr__(self, key):
    if key not in self.entries:
      raise Exception('No such key: %s' % key)
    return self.entries[key]

  def put(self, key, value):
    if key in self.entries:
      logging.warn('changing value of %s' % key)
    self.entries[key] = value

  def __repr__(self):
    return '%s(%d items)' % (self.__class__, len(self.keys))

  def __str__(self):
    s = []
    s.append('%s:' % self.__class__.__name__)
    for key in sorted(self.entries.keys()):
      s.append('  %s: %s' % (key, getattr(self, key)))
    return '\n'.join(s)
