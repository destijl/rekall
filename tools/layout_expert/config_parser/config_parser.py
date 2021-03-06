"""A module containing a parser for parsing Linux kernel .config files."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
from rekall.layout_expert.c_ast import c_ast


class ConfigParser(object):
  """A class for parsing Linux kernel .config files."""

  def __init__(self):
    flag = r'(?P<flag>\w+)'
    value = r'(?P<value>[^\n]*)'
    self._flag_and_value_regex = re.compile(r'^' + flag + r'=' + value + r'$')

  def parse(self, config):
    """A method for parsing Linux kernel .config files.

    Args:
      config: a string with the content of a Linux kernel .config file.

    Returns:
      A dict from flag names to flag values for the defined flags.

    Raises:
      UnknownConfigLineFormatException: raised when the line format is not
        recognised by the parser.
    """
    flags = {}
    for line in config.split('\n'):
      match = self._flag_and_value_regex.match(line)
      if match:
        self._process_flag_and_value_line(line, match, flags)
      elif not line or line.isspace() or line[0] == '#':
        pass
      else:
        raise UnknownConfigLineFormatException(line)

    return flags

  def _process_flag_and_value_line(self, line, match, flags):
    flag = match.group('flag')
    value = match.group('value')
    try:
      if value == 'm':
        flags[flag + '_MODULE'] = c_ast.CNumber(1)
      else:
        flags[flag] = self._parse_value(value)
    except ValueError:
      raise UnknownConfigLineFormatException(line)

  def _parse_value(self, value):
    if value == 'y':
      return c_ast.CNumber(1)
    elif len(value) >= 2 and value[0] == '"' and value[-1] == '"':
      return c_ast.CLiteral(value[1:-1])
    else:
      return c_ast.CNumber(int(value, base=0))  # Throws ValueError.


class UnknownConfigLineFormatException(Exception):
  pass
