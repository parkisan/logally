#! /usr/bin/python


from PyQt4.QtGui import *
from PyQt4.QtCore import *

from logally.lib import utils


import functools
import datetime_tz


class DataType(object):
  __metaclass__ = utils.MetaclassRegistry

  def __init__(self, initial_value=None):
    self.value = self.Canonicalize(initial_value)

  @classmethod
  def IsCanonical(cls, value=None):
    """Whether value is a canonical value or not."""

  @classmethod
  def Canonicalize(cls, value=None):
    """Tries to fit the given value into a canonical value."""

  @classmethod
  def Encode(cls, value=None):
    """Takes a value and returns the on-the-wire equivalent."""
    canonical_value = value
    if not cls.IsCanonical(value):
      try:
        canonical_value = cls.Canonicalize(value)
      except ValueError:
        raise ValueError('%s is not a valid canonical value.')
    return cls._Encoded(canonical_value)

  @classmethod
  def _Encoded(cls, value=None):
    """Takes a canonical value and returns the on-the-wire equivalent."""

  @classmethod
  def Decode(cls, value=None):
    """Takes an encoded value and returns a canonical value."""

  def __repr__(self):
    return str(self)

  def __str__(self):
    return "%s(%s)" % (self.__class__.__name__,
                       self.value)


class NoType(DataType):
  @classmethod
  def IsCanonical(cls, value=None):
    return True

  @classmethod
  def _Encoded(cls, value):
    return value

  @classmethod
  def Decode(cls, value):
    return value


@functools.total_ordering
class DatetimeType(DataType):
  @classmethod
  def IsCanonical(cls, value=None):
    return isinstance(value, datetime_tz.datetime_tz)

  @classmethod
  def Canonicalize(cls, value=None):
    if type(value) in (int, long):
      return datetime_tz.datetime_tz.utcfromtimestamp(value)
    try:
      return datetime_tz.datetime_tz.smartparse(value)
    except (ValueError, AttributeError):
      raise ValueError("Invalid value %s (%s)for a %s." %
                       (value, type(value), cls.__name__))

  @classmethod
  def _Encoded(cls, value):
    return value.totimestamp() * 1e6

  @classmethod
  def Decode(cls, value):
    return datetime_tz.datetime_tz.utcfromtimestamp(value / 1e6)

  def __lt__(self, other):
    print "Comparing %s < %s" % (self.value, other.value)
    return self.value < other.value

  def __eq__(self, other):
    return self.value == other.value

  def __str__(self):
    return str(self.value)


class UTF8StringType(DataType):
  def __init__(self, *args, **kwargs):
    super(UTF8StringType, self).__init__(*args, **kwargs)
    self._gui_options = {
      'maxlength': 0,
      'validator': None,
    }

  @classmethod
  def IsCanonical(cls, value=None):
    return isinstance(value, unicode)

  @classmethod
  def Canonicalize(cls, value=None):
    return unicode(value)

  @classmethod
  def _Encoded(cls, value=None):
    return utils.SmartUnicode(value)

  @classmethod
  def Decode(cls, value=None):
    return unicode(value)

  def RenderQtForm(self, layout, name=None, row=0):
    default_value = self._gui_options.get('default')
    self.label = QLabel(name)
    self.label.setTextFormat(Qt.RichText)
    layout.addWidget(self.label, row, 0)
    self.text_input = QLineEdit()
    self.text_input.setText(default_value)
    if self._gui_options['maxlength']:
      self.text_input.setMaxLength(self._gui_options['maxlength'])
    layout.addWidget(self.text_input, row, 1)

  def SetValueFromQt(self):
    self.value = unicode(self.text_input.text())


class FilenameType(UTF8StringType):
  def RenderQtForm(self, layout, name=None, row=0):
    self.push_button = QPushButton("File:")
    self.label = QLabel("[No file selected]")
    layout.addWidget(self.push_button, 0, 0)
    layout.addWidget(self.label, 0, 1)
    layout.connect(self.push_button,
                   SIGNAL("clicked()"),
                   self._OpenFileCallback)

  def _OpenFileCallback(self):
    old_value = self.label.text()
    filename = QFileDialog.getOpenFileName(None, "Choose a file", "", "*.*")
    if not filename:
      filename = old_value
    else:
      self.value = filename
    self.label.setText(filename)


  def SetValueFromQt(self):
    pass
