from PyQt4.QtCore import *
from PyQt4.QtGui import *

from logally import model
from logally.qt import tableview
from logally.lib import index

class TableViewPresenter(QObject):
  def __init__(self, exploration=None, table=None, parent=None):
    super(TableViewPresenter, self).__init__(parent)
    self.exploration = exploration
    self.table = table
    try:
      self.table.Open()
    except model.TableNotIndexedError:
      fd = open("test_index", "w")
      metaindex = index.MetaTableIndex()
      metaindex.Save(file_obj=fd, metatable=table)
      self.table.SetIndex(metaindex=metaindex)
      fd.close()
      fd = open("test_index", "r")
      metaindex.Load(file_obj=fd)
      self.table.SetIndex(metaindex=metaindex)
    self.table.Open()
    table_model = TableModel(table=self.table)
    self.view = TableViewWindow(presenter=self, parent=parent)
    self.view.setWindowTitle(
      ': '.join([self.exploration.name, self.table.name]))
    self.view.ui.tableView.setModel(table_model)
    self.view.ui.tableView.setAlternatingRowColors(True)
    self.view.ui.tableView.horizontalHeader().setStretchLastSection(True)
    #self.view.ui.tableView.horizontalHeader().setResizeMode(
    #    QHeaderView.ResizeToContents)
    #self.setAttribute(Qt.WA_DeleteOnClose)
    self.rowCountChanged(rows=self.table.row_count)
    self.view.show()

  def rowCountChanged(self, rows=0):
    row_msg = "Rows: %s" % str(rows)
    self.view.ui.rowcountLabel.setText(row_msg)


  def __del__(self):
    print "presenter bye"


class TableViewWindow(QMainWindow):
  def __init__(self, presenter=None, parent=None):
    super(TableViewWindow, self).__init__(parent)
    #self.presenter = presenter
    self.ui = tableview.Ui_TableViewWindow()
    self.ui.setupUi(self)
    self.ui.rowcountLabel = QLabel(None)
    self.ui.statusbar.addWidget(self.ui.rowcountLabel)
    self.setAttribute(Qt.WA_DeleteOnClose)


class TableModel(QAbstractTableModel):
  def __init__(self, table=None):
    super(TableModel, self).__init__()
    self.table = table

  def headerData(self, section, orientation, role):
    if role != Qt.DisplayRole:
      return QVariant()
    if orientation == Qt.Horizontal:
      # Show the column names
      column = self.table.ColumnAt(index=section)
      return QVariant(column.name)
    elif orientation == Qt.Vertical:
      # Show the row header, for now just the order
      return QVariant(section)
    return QVariant()

  def data(self, index, role):
    #TODO(parki): Format the cell
    if role != Qt.DisplayRole:
      return QVariant()
    try:
      cell = self.table.Cell(column_index=index.column(), row_index=index.row())
      return QVariant(unicode(cell.value))
    except IndexError:
      return QVariant()

  def columnCount(self, parent):
    return self.table.column_count

  def rowCount(self, parent):
    return self.table.row_count

  def index(self, row, column, parent):
    return self.createIndex(row, column)

  def parent(self, child):
    return self

  def flags(self, index):
    if not index.isValid():
      return Qt.ItemIsEnabled
    return Qt.ItemIsEnabled
