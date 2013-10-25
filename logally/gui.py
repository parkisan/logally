#! /usr/bin/python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qt import main


class MainWindow(QMainWindow):
  def __init__(self, presenter=None, parent=None):
    QMainWindow.__init__(self, parent=parent)
    self.ui = main.Ui_MainWindow()
    self.ui.setupUi(self)
    self.presenter = presenter
    self.ui.treeView.setModel(self.presenter.explorationtreemodel)
    self.ui.actionExit.triggered.connect(self.presenter.onExit)
    self.ui.actionNew.triggered.connect(self.presenter.onNew)
    self.ui.actionOpen.triggered.connect(self.presenter.onOpen)
    self.ui.actionNewDatasource.triggered.connect(
      self.presenter.onAddNewDatasourceDialog)
    self.ui.actionNewTable.triggered.connect(
      self.presenter.onAddNewTableDialog)
    self.ui.actionSave.triggered.connect(self.presenter.onSave)
    self.ui.actionSaveAs.triggered.connect(self.presenter.onSaveAs)
    self.ui.treeView.doubleClicked.connect(self.presenter.onTreeDoubleclick)


class MetaTableModel(QAbstractTableModel):
  def __init__(self, metatable=None):
    self.metatable = metatable

  def headerData(self, section, orientation, role):
    if role != Qt.DisplayRole:
      return QVariant()
    if orientation == Qt.Horizontal:
      return QVariant(str(self.headers[section]))
    elif orientation == Qt.Vertical:
      return QVariant(section)
    return QVariant()

  def data(self, index, role):
    if role != Qt.DisplayRole:
      return QVariant()
    try:
      cell = self.metatable.Cell(meta_column_index=index.column(), meta_row_index=index.row())
      return QVariant(cell)
    except IndexError:
      return QVariant()

  def columnCount(self, parent):
    return self.metatable.column_count

  def rowCount(self, parent):
    return self.metatable.row_count

  def index(self, row, column, parent):
    return self.createIndex(row, column)

  def parent(self, child):
    return self

  def flags(self, index):
    if not index.isValid():
      return Qt.ItemIsEnabled
    return Qt.ItemIsEnabled
