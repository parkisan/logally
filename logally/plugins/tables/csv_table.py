#! /usr/bin/python

import csv

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from logally import model
from logally.lib import datatypes


class SingleCharacterInput(datatypes.UTF8StringType):
  # TODO(park): Move to datatypes.
  def __init__(self, *args, **kwargs):
    super(SingleCharacterInput, self).__init__(*args, **kwargs)
    self._gui_options['maxlength'] = 1
    self._gui_options['validator'] = self.ValidateAndEscape
    if self._default_value:
      self._gui_options['default'] = self._default_value

  def ValidateAndEscape(self):
    try:
      self.value = self.value.decode("unicode_escape")
    except UnicodeDecodeError:
      return False
    return True


class DelimiterType(SingleCharacterInput):
  _default_value = u","


class QuoteCharType(SingleCharacterInput):
  _default_value = u'"'


class EscapeCharType(SingleCharacterInput):
  _default_value = u"\\\\"


class LineTerminatorType(SingleCharacterInput):
  _default_value = u"\\r\\n"

  def __init__(self, *args, **kwargs):
    super(LineTerminatorType, self).__init__(*args, **kwargs)
    self._gui_options['maxlength'] = 0


class CsvTable(model.Table):
  valid_parameters = {
    'delimiter': DelimiterType,
    'quotechar': QuoteCharType,
    'escapechar': EscapeCharType,
    'lineterminator': LineTerminatorType,
    #'doublequote': datatypes.BooleanType,
  }

  def __init__(self, name=None, delimiter=',', quotechar='"',
               doublequote=False, escapechar=None, lineterminator='\r'):
    super(CsvTable, self).__init__(name)
    self._data = []
    self._is_loaded = False
    self.delimiter = delimiter
    self.quotechar = quotechar
    self.doublequote = doublequote
    self.escapechar = escapechar
    self.lineterminator = lineterminator

  def Open(self):
    if self.is_open:
      return True

    if not self.datasource:
      raise ValueError("No datasource selected.")
    self.datasource.Open()
    self.csv_reader = csv.reader(self.datasource,
                                 delimiter=self.delimiter,
                                 quotechar=self.quotechar,
                                 doublequote=self.doublequote,
                                 escapechar=self.escapechar,
                                 lineterminator=self.lineterminator)
    header = self.csv_reader.next()
    for col in header:
      column = model.Column(name=col, datatype=datatypes.NoType)
      self.AppendColumn(column=column)
    self.headers = header
    self._row_count = 0
    print self.columns
    self.is_open = True

  @property
  def row_count(self):
    self._LoadData()
    return len(self._data)

  @row_count.setter
  def row_count(self, value):
    self._row_count = value

  def _LoadData(self):
    rows = 0
    if not self._is_loaded:
      for line in self.csv_reader:
        self._data.append(line)
        rows += 1
    self._is_loaded = True
    self.row_count = rows

  def Cell(self, row_index=0, column_index=0):
    self._LoadData()
    return model.Cell(value=self._data[row_index][column_index],
                      column=self.ColumnAt(index=column_index))
