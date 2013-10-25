# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/Main.ui'
#
# Created: Thu Oct 18 16:13:39 2012
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui


class Ui_MainWindow(object):
  def setupUi(self, MainWindow):
    MainWindow.setObjectName("MainWindow")
    MainWindow.resize(580, 563)
    self.centralwidget = QtGui.QWidget(MainWindow)
    self.centralwidget.setObjectName("centralwidget")
    self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
    self.verticalLayout.setObjectName("verticalLayout")
    self.splitter = QtGui.QSplitter(self.centralwidget)
    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum,
                                   QtGui.QSizePolicy.Preferred)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
    self.splitter.setSizePolicy(sizePolicy)
    self.splitter.setOrientation(QtCore.Qt.Horizontal)
    self.splitter.setObjectName("splitter")
    self.treeView = QtGui.QTreeView(self.splitter)
    self.treeView.setObjectName("treeView")
    self.tableView = QtGui.QTableView(self.splitter)
    self.tableView.setObjectName("tableView")
    self.verticalLayout.addWidget(self.splitter)
    MainWindow.setCentralWidget(self.centralwidget)
    self.menubar = QtGui.QMenuBar(MainWindow)
    self.menubar.setGeometry(QtCore.QRect(0, 0, 580, 21))
    self.menubar.setObjectName("menubar")
    self.menu_File = QtGui.QMenu(self.menubar)
    self.menu_File.setObjectName("menu_File")
    self.menuHelp = QtGui.QMenu(self.menubar)
    self.menuHelp.setObjectName("menuHelp")
    MainWindow.setMenuBar(self.menubar)
    self.statusbar = QtGui.QStatusBar(MainWindow)
    self.statusbar.setObjectName("statusbar")
    MainWindow.setStatusBar(self.statusbar)
    self.toolBar = QtGui.QToolBar(MainWindow)
    self.toolBar.setObjectName("toolBar")
    MainWindow.addToolBar(QtCore.Qt.ToolBarArea(QtCore.Qt.TopToolBarArea),
                          self.toolBar)
    self.actionNew = QtGui.QAction(MainWindow)
    self.actionNew.setObjectName("actionNew")
    self.actionOpen = QtGui.QAction(MainWindow)
    self.actionOpen.setObjectName("actionOpen")
    self.actionSave = QtGui.QAction(MainWindow)
    self.actionSave.setObjectName("actionSave")
    self.actionExit = QtGui.QAction(MainWindow)
    self.actionExit.setObjectName("actionExit")
    self.actionAbout = QtGui.QAction(MainWindow)
    self.actionAbout.setObjectName("actionAbout")
    self.actionSaveAs = QtGui.QAction(MainWindow)
    self.actionSaveAs.setObjectName("actionSaveAs")
    self.actionNewDatasource = QtGui.QAction(MainWindow)
    self.actionNewDatasource.setObjectName("actionNewDatasource")
    self.actionNewTable = QtGui.QAction(MainWindow)
    self.actionNewTable.setObjectName("actionNewTable")
    self.menu_File.addAction(self.actionNew)
    self.menu_File.addAction(self.actionOpen)
    self.menu_File.addSeparator()
    self.menu_File.addAction(self.actionNewDatasource)
    self.menu_File.addAction(self.actionNewTable)
    self.menu_File.addSeparator()
    self.menu_File.addAction(self.actionSave)
    self.menu_File.addAction(self.actionSaveAs)
    self.menu_File.addSeparator()
    self.menu_File.addAction(self.actionExit)
    self.menuHelp.addAction(self.actionAbout)
    self.menubar.addAction(self.menu_File.menuAction())
    self.menubar.addAction(self.menuHelp.menuAction())

    self.retranslateUi(MainWindow)
    QtCore.QMetaObject.connectSlotsByName(MainWindow)

  def retranslateUi(self, MainWindow):
    MainWindow.setWindowTitle(
      QtGui.QApplication.translate("MainWindow", "MainWindow", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.menu_File.setTitle(
      QtGui.QApplication.translate("MainWindow", "&File", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.menuHelp.setTitle(
      QtGui.QApplication.translate("MainWindow", "&Help", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.toolBar.setWindowTitle(
      QtGui.QApplication.translate("MainWindow", "toolBar", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.actionNew.setText(
      QtGui.QApplication.translate("MainWindow", "&New...", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.actionNew.setShortcut(
      QtGui.QApplication.translate("MainWindow", "Ctrl+N", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.actionOpen.setText(
      QtGui.QApplication.translate("MainWindow", "&Open...", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.actionOpen.setShortcut(
      QtGui.QApplication.translate("MainWindow", "Ctrl+O", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.actionSave.setText(
      QtGui.QApplication.translate("MainWindow", "&Save...", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.actionSave.setShortcut(
      QtGui.QApplication.translate("MainWindow", "Ctrl+S", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.actionExit.setText(
      QtGui.QApplication.translate("MainWindow", "E&xit", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.actionExit.setShortcut(
      QtGui.QApplication.translate("MainWindow", "Ctrl+Q", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.actionAbout.setText(
      QtGui.QApplication.translate("MainWindow", "&About", None,
                                   QtGui.QApplication.UnicodeUTF8))
    self.actionSaveAs.setText(
      QtGui.QApplication.translate("MainWindow", "Save &As...", None,
                                   QtGui.QApplication.UnicodeUTF8))

    self.actionNewDatasource.setText(
      QtGui.QApplication.translate("MainWindow", "New &Datasource...", None,
                                   QtGui.QApplication.UnicodeUTF8))

    self.actionNewDatasource.setShortcut(
      QtGui.QApplication.translate("MainWindow", "Ctrl+D", None,
                                   QtGui.QApplication.UnicodeUTF8))

    self.actionNewTable.setText(
      QtGui.QApplication.translate("MainWindow", "New &Table...", None,
                                   QtGui.QApplication.UnicodeUTF8))

    self.actionNewTable.setShortcut(
      QtGui.QApplication.translate("MainWindow", "Ctrl+T", None,
                                   QtGui.QApplication.UnicodeUTF8))

