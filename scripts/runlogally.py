#!/usr/bin/python

import logging
import sys

from PyQt4.QtGui import *
from logally import gui
from logally import model
from logally.qt import main_presenter


if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)
  app = QApplication(sys.argv)
  presenter = main_presenter.MainPresenter(model=model)
  main = gui.MainWindow(presenter=presenter)
  presenter.setView(view=main)
  main.show()
  sys.exit(app.exec_())
