#! /usr/bin/python

import abc
import uuid


class MetaclassRegistry(abc.ABCMeta):
  """Automatic Plugin Registration through metaclasses."""

  def __init__(mcs, name, bases, env_dict):
    abc.ABCMeta.__init__(mcs, name, bases, env_dict)

    # Abstract classes should not be registered. We define classes as
    # abstract by giving them the __abstract attribute (this is not
    # inheritable) or by naming them Abstract<ClassName>.
    abstract_attribute = "_%s__abstract" % name

    if (not mcs.__name__.startswith("Abstract") and
          not hasattr(mcs, abstract_attribute)):
      # Attach the classes dict to the baseclass and have all derived
      # classes use the same one:
      for base in bases:
        try:
          mcs.classes = base.classes
          mcs.plugin_feature = base.plugin_feature
          mcs.top_level_class = base.top_level_class
          break
        except AttributeError:
          pass

      try:
        mcs.classes[mcs.__name__] = mcs
        mcs.class_list.append(mcs)
      except AttributeError:
        mcs.classes = {mcs.__name__: mcs}
        mcs.class_list = [mcs]
        mcs.plugin_feature = mcs.__name__
        # Keep a reference to the top level class
        mcs.top_level_class = mcs

      try:
        if mcs.top_level_class.include_plugins_as_attributes:
          setattr(mcs.top_level_class, mcs.__name__, mcs)

      except AttributeError:
        pass


class Sender(object):
  def __init__(self):
    self._observers_by_signal = {}

  def signal(self, signal_name=None, *args, **kwargs):
    if not signal_name:
      raise ValueError("Invalid signal name '%s'." % signal_name)
    for observer in self._observers_by_signal.get(signal_name, []):
      observer(*args, **kwargs)

  def connect(self, signal_name=None, observer=None):
    if not signal_name:
      raise ValueError("Invalid signal name '%s'." % signal_name)
    signal = self._observers_by_signal.setdefault(signal_name, [])
    signal.append(observer)

  def disconnect(self, signal_name=None, observer=None):
    observers_for_signal = self._observers_by_signal.get(signal_name)
    if observers_for_signal:
      observers_for_signal.remove(observer)


class UUID(object):
  def __init__(self, from_value=None):
    if not from_value:
      self.value = uuid.uuid4()
    else:
      try:
        self.value = uuid.UUID(from_value)
      except ValueError:
        self.value = uuid.UUID(bytes=from_value)
      except AttributeError:
        raise ValueError("Invalid UUID value %r." % from_value)

  @property
  def hex(self):
    return self.value.hex

  @property
  def int(self):
    return self.value.int

  @property
  def bytes(self):
    return self.value.bytes

  @property
  def fields(self):
    return self.value.fields

  def __eq__(self, other):
    if isinstance(other, UUID):
      return self.int == other.int

def random_uuid():
  return uuid.uuid4()


# Borrowed from http://grr.googlecode.com/git/lib/utils.py
def SmartUnicode(string):
  """Returns a unicode object.

  This function will always return a unicode object. It should be used to
  guarantee that something is always a unicode object.

  Args:
    string: The string to convert.

  Returns:
    a unicode object.
  """
  if type(string) != unicode:
    try:
      return string.__unicode__()
    except (AttributeError, UnicodeError):
      return str(string).decode("utf8", "ignore")

  return string


def Proxy(f):
  """A helper to create a proxy method in a class."""

  def Wrapped(self, *args):
    return getattr(self, f)(*args)

  return Wrapped
