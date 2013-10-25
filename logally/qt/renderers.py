from PyQt4.QtGui import *

from logally.lib import
from logally.lib import datatypes

class Renderer(object):
  datatype = None

  def Render(self, value):
    pass


class FilenameRenderer(object):
  datatype = datatypes.FilenameType

  def RenderQtForm(self, layout):
    self.push_button = QPushButton("FIle:")
    self.label = QLabel("[No file selected]")
    layout.addWidget(self.push_button, 0, 0)
    layout.addWidget(self.label, 0, 1)
    layout.connect(self.push_button, "clicked()", self._OpenFileCallback)

  def _OpenFileCallback(self):
    old_value = self.label.text()
    filename = QFileDialod.getOpenFileName(None, "Choose a file", "", "*.*")
    if not filename:
      filename = old_value
    self.label.setText(filename)
