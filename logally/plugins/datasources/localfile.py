from logally import model
from logally.lib import datatypes, utils


class LocalFile(model.DataSource):
  __metaclass__ = utils.MetaclassRegistry
  valid_parameters = {"path": datatypes.FilenameType}

  def __init__(self, name=None, uuid=None):
    super(LocalFile, self).__init__(name=name, uuid=uuid)
    self.fd = None

  def Open(self):
    if not self.parameters.get("path", None):
      raise ValueError("No path specified.")

    self.fd = open(self.parameters.get("path"), "r")

  def Read(self, size=0):
    if self.fd:
      return self.fd.read(size)
    else:
      raise IOError()

  read = utils.Proxy("Read")

  def readlines(self, *args):
    return self.fd.readlines(*args)

  def readline(self, *args):
    return self.fd.readline(*args)

  def __iter__(self):
    return self.fd.__iter__()

  def seek(self, offset, whence):
    return self.fd.seek(offset, whence)

  def tell(self):
    return self.fd.tell()
