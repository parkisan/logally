# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/TableView.ui'
#
# Created: Mon Oct 22 00:18:30 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
  _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
  _fromUtf8 = lambda s: s


class Ui_TableViewWindow(object):
  def setupUi(self, TableViewWindow):
    TableViewWindow.setObjectName(_fromUtf8("TableViewWindow"))
    TableViewWindow.resize(864, 790)
    self.centralwidget = QtGui.QWidget(TableViewWindow)
    self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
    self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
    self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
    self.verticalLayout = QtGui.QVBoxLayout()
    self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
    self.verticalLayout_2 = QtGui.QVBoxLayout()
    self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
    self.tableView = QtGui.QTableView(self.centralwidget)
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum,
                                   QtGui.QSizePolicy.Expanding)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(
      self.tableView.sizePolicy().hasHeightForWidth())
    self.tableView.setSizePolicy(sizePolicy)
    self.tableView.setObjectName(_fromUtf8("tableView"))
    self.verticalLayout_2.addWidget(self.tableView)
    self.pushButton = QtGui.QPushButton(self.centralwidget)
    self.pushButton.setObjectName(_fromUtf8("pushButton"))
    self.verticalLayout_2.addWidget(self.pushButton)
    self.verticalLayout.addLayout(self.verticalLayout_2)
    self.horizontalLayout.addLayout(self.verticalLayout)
    self.optionsTabs = QtGui.QTabWidget(self.centralwidget)
    self.optionsTabs.setEnabled(True)
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum,
                                   QtGui.QSizePolicy.Expanding)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(
      self.optionsTabs.sizePolicy().hasHeightForWidth())
    self.optionsTabs.setSizePolicy(sizePolicy)
    self.optionsTabs.setTabsClosable(False)
    self.optionsTabs.setMovable(False)
    self.optionsTabs.setObjectName(_fromUtf8("optionsTabs"))
    self.filters = QtGui.QWidget()
    self.filters.setObjectName(_fromUtf8("filters"))
    self.verticalLayout_4 = QtGui.QVBoxLayout(self.filters)
    self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
    self.verticalLayout_3 = QtGui.QVBoxLayout()
    self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
    self.listView = QtGui.QListView(self.filters)
    self.listView.setObjectName(_fromUtf8("listView"))
    self.verticalLayout_3.addWidget(self.listView)
    self.verticalLayout_4.addLayout(self.verticalLayout_3)
    self.optionsTabs.addTab(self.filters, _fromUtf8(""))
    self.highlights = QtGui.QWidget()
    self.highlights.setObjectName(_fromUtf8("highlights"))
    self.verticalLayout_6 = QtGui.QVBoxLayout(self.highlights)
    self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
    self.verticalLayout_5 = QtGui.QVBoxLayout()
    self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
    self.listWidget = QtGui.QListWidget(self.highlights)
    self.listWidget.setObjectName(_fromUtf8("listWidget"))
    self.verticalLayout_5.addWidget(self.listWidget)
    self.verticalLayout_6.addLayout(self.verticalLayout_5)
    self.optionsTabs.addTab(self.highlights, _fromUtf8(""))
    self.horizontalLayout.addWidget(self.optionsTabs)
    TableViewWindow.setCentralWidget(self.centralwidget)
    self.menubar = QtGui.QMenuBar(TableViewWindow)
    self.menubar.setGeometry(QtCore.QRect(0, 0, 864, 22))
    self.menubar.setObjectName(_fromUtf8("menubar"))
    self.menuTable = QtGui.QMenu(self.menubar)
    self.menuTable.setObjectName(_fromUtf8("menuTable"))
    TableViewWindow.setMenuBar(self.menubar)
    self.statusbar = QtGui.QStatusBar(TableViewWindow)
    self.statusbar.setObjectName(_fromUtf8("statusbar"))
    TableViewWindow.setStatusBar(self.statusbar)
    self.actionClose = QtGui.QAction(TableViewWindow)
    self.actionClose.setObjectName(_fromUtf8("actionClose"))
    self.menuTable.addAction(self.actionClose)
    self.menubar.addAction(self.menuTable.menuAction())

    self.retranslateUi(TableViewWindow)
    self.optionsTabs.setCurrentIndex(0)
    QtCore.QObject.connect(self.actionClose,
                           QtCore.SIGNAL(_fromUtf8("triggered()")),
                           TableViewWindow.close)
    QtCore.QMetaObject.connectSlotsByName(TableViewWindow)

  def retranslateUi(self, TableViewWindow):
    TableViewWindow.setWindowTitle(
      QtGui.QApplication.translate("TableViewWindow", "MainWindow", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.pushButton.setText(
      QtGui.QApplication.translate("TableViewWindow", "Show/Hide Options", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.optionsTabs.setTabText(self.optionsTabs.indexOf(self.filters),
                                QtGui.QApplication.translate("TableViewWindow",
                                                             "Filters", None,
                                                             QtGui
                                                             .QApplication
                                                             .UnicodeUTF8))
    self.optionsTabs.setTabText(self.optionsTabs.indexOf(self.highlights),
                                QtGui.QApplication.translate("TableViewWindow",
                                                             "Highlights", None,
                                                             QtGui
                                                             .QApplication
                                                             .UnicodeUTF8))
    self.menuTable.setTitle(
      QtGui.QApplication.translate("TableViewWindow", "&Table", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.actionClose.setText(
      QtGui.QApplication.translate("TableViewWindow", "&Close", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.actionClose.setShortcut(
      QtGui.QApplication.translate("TableViewWindow", "Ctrl+Q", None,
                                   QtGui.QApplication.UnicodeUTF8))

