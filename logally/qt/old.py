#! /usr/bin/python

import sip

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import model


try:
  _fromUtf8 = QString.fromUtf8
except AttributeError:
  _fromUtf8 = lambda s: s


class AddNewDataSourceDialog(QDialog):
  def __init__(self, parent):
    super(AddNewDataSourceDialog, self).__init__(parent)
    self.setAttribute(Qt.WA_DeleteOnClose)
    sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    self.setSizePolicy(sizePolicy)
    self.vboxLayout = QVBoxLayout()
    self.setLayout(self.vboxLayout)
    self.comboBox = QComboBox()
    self.comboBox.addItem(QString(''))
    for cls in sorted(DataSource.classes):
      if cls != DataSource.__name__:
        self.comboBox.addItem(QString(cls), QVariant())
    self.connect(self.comboBox, SIGNAL("currentIndexChanged(QString)"),
                 self.updateSourceConfig)
    self.vboxLayout.addWidget(self.comboBox)
    self.dataSourceLayout = QVBoxLayout()
    self.dataSourceWidget = QWidget()
    self.dataSourceWidget.setLayout(self.dataSourceLayout)
    self.vboxLayout.addWidget(self.dataSourceWidget)
    self.hboxLayout = QHBoxLayout()
    self.vboxLayout.addLayout(self.hboxLayout)
    self.hboxLayout.setSizeConstraint(QLayout.SetMaximumSize)
    self.applyButton = QPushButton('Add', self)
    self.quitButton = QPushButton('Quit', self)
    maxSizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
    self.applyButton.setSizePolicy(maxSizePolicy)
    self.quitButton.setSizePolicy(maxSizePolicy)
    self.hboxLayout.addWidget(self.applyButton)
    self.hboxLayout.addWidget(self.quitButton)
    self.connect(self.quitButton, SIGNAL('clicked()'), self.close)
    self.setWindowTitle("Add data source")

  def updateSourceConfig(self, datasource_name):
    sip.delete(self.dataSourceWidget)
    self.dataSourceLayout = QVBoxLayout()
    self.dataSourceWidget = QWidget()
    self.dataSourceWidget.setLayout(self.dataSourceLayout)
    self.vboxLayout.insertWidget(1, self.dataSourceWidget)
    # delete first
    try:
      self.input_source = model.DataSource.classes[datasource_name]()
    except KeyError:
      print "..."
    self.input_source.setupUi(self.dataSourceLayout)


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


class OnesModel(QAbstractTableModel):
  def __init__(self, table=None, max_rows=None):
    QAbstractTableModel.__init__(self)
    self.data = []

    print 'Opening %s from ' % csvfile
    fd = open(csvfile, 'r')
    self.csv_reader = csv.reader(fd, dialect=MyDialect)
    header = self.csv_reader.next()
    self.columns = len(header)
    self.headers = header
    self.rows = 0
    print self.headers
    for line in self.csv_reader:
      #print line
      self.data.append(line)
      self.rows += 1
      if max_rows and self.rows == max_rows:
        break

  def InsertRows(self, first, last, parent):
    self.beginInsertRows(QModelIndex(), first, last - 1)
    self.rows += last - first
    self.endInsertRows()

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
      return QVariant(self.data[index.row()][index.column()])
    except IndexError:
      return QVariant()

  def columnCount(self, parent):
    return self.columns

  def rowCount(self, parent):
    return self.rows

  def index(self, row, column, parent):
    return self.createIndex(row, column)

  def parent(self, child):
    return self

  def flags(self, index):
    if not index.isValid():
      return Qt.ItemIsEnabled
    return Qt.ItemIsEnabled


class MainWindow(QMainWindow):
  def __init__(self):
    QMainWindow.__init__(self)

    dummy_widget = QWidget()
    dummy_widget.setSizePolicy(
      QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
    vbox = QVBoxLayout()
    self.tableWidget = QTableView()
    self.tableWidget.horizontalHeader().setStretchLastSection(True)
    self.tableWidget.horizontalHeader().setResizeMode(
      QHeaderView.ResizeToContents)
    self.tableModel = model.OnesModel('test2.csv')
    #self.tableModel.insertColumn(1)
    self.tableWidget.setModel(self.tableModel)
    self.tableWidget.setItemDelegate(QItemDelegate())
    #self.tableWidget.setRowCount(long(1e7));
    #self.tableWidget.setColumnCount(10);
    vbox.addWidget(self.tableWidget)
    quitbutton = QPushButton('Close', self)
    self.connect(quitbutton, SIGNAL('clicked()'), SLOT('close()'))
    dummy_widget.setLayout(vbox)
    self.setCentralWidget(dummy_widget)
    addrow_btn = QPushButton('Add 1 row', self)
    addsource_btn = QPushButton('Add datasource', self)
    self.connect(addrow_btn, SIGNAL('clicked()'), self.addRow)
    self.connect(addsource_btn, SIGNAL('clicked()'), self.addDataSource)
    self.statusbar = QStatusBar(self)
    self.setStatusBar(self.statusbar)
    vbox.addWidget(addrow_btn)
    vbox.addWidget(addsource_btn)
    vbox.addWidget(quitbutton)

  def addRow(self):
    print 'Adding row'
    self.tableModel.insertRows(0, 1, QModelIndex())
    print self.tableModel.rowCount(None)

  def addDataSource(self):
    dialog = AddNewDataSourceDialog(self)
    if dialog.exec_():
      print "Done"
    else:
      print "Closed"

  def rowCountChanged(self, old, new):
    print "Row count changed from %s to %s" % (old, new)
