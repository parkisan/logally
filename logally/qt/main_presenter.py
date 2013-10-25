from PyQt4.QtCore import *
from PyQt4.QtGui import *

from logally.qt import tableview_presenter
from logally.plugins.tables import csv_table
from logally.plugins.datasources.localfile import LocalFile
from logally.lib import datatypes
from logally import model

import sip


class MainPresenter(QObject):
  def __init__(self, model=None, parent=None):
    QObject.__init__(self, parent)
    self.model = model
    self.exploration = self.model.Exploration(name="Test exploration")
    self.metatable = self.model.MetaTable(name="Test metatable")
    #datasource = LocalFile(name="paso_test")
    #datasource.SetParameter(name="path", value="plaso_test")
    datasource = LocalFile(name="test.csv")
    datasource.SetParameter(name="path", value="test.csv")
    datasource2 = LocalFile(name="test2.csv")
    datasource2.SetParameter(name="path", value="test2.csv")
    table = model.Table.classes["CsvTable"](name="Test table", delimiter="\t")
    #table = model.Table.classes["PlasoTable"](name="Test table")
    table.SetDataSource(datasource=datasource)
    table.Open()
    table.ColumnAt(0).type = datatypes.DatetimeType
    table.SetOrderColumn(0)
    table2 = model.Table.classes["CsvTable"](name="Test table 2",
                                             delimiter="\t")
    table2.SetDataSource(datasource=datasource2)
    table2.Open()
    table2.ColumnAt(0).type = datatypes.DatetimeType
    table2.SetOrderColumn(0)
    for (column, column2) in zip(table.columns, table2.columns):
    #for column in table.columns:
      metacolumn = model.MetaColumn(name=column.name, datatype=column.type)
      metacolumn.SetReference(table=table, column=column)
      metacolumn.SetReference(table=table2, column=column2)
      self.metatable.AppendColumn(column=metacolumn)
    self.metatable.ColumnAt(0).type = datatypes.DatetimeType
    print "Column0 references: %s" % self.metatable.ColumnAt(0).references
    print "Column1 references: %s" % self.metatable.ColumnAt(1).references
    print self.metatable.tables
    #self.metatable.AddTable(table=table)
    self.metatable.SetOrderColumn(0)
    print "Order column: %s (%s)" % (self.metatable.OrderColumn(),
                                     self.metatable.OrderColumn().type)
    self.exploration.AddTable(table=table)
    self.exploration.AddTable(table=table2)
    self.exploration.AddDataSource(datasource=datasource)
    self.exploration.AddDataSource(datasource=datasource2)
    self.exploration.AddMetaTable(metatable=self.metatable)
    self.explorationtreemodel = ExplorationModel(exploration=self.exploration)
    self.view = None
    print table.Cell(0,0).value
    #self.presenters = []


  def setView(self, view=None):
    self.view = view

  def onExit(self):
    self.onSave()
    self.view.close()

  def onNew(self):
    pass

  def onOpen(self):
    filename = self._GetExplorationFileFromUser()
    if filename:
      try:
        self.exploration = self.model.Exploration.Load(filename=filename)
      except ValueError as e:
        raise ("Invalid exploration file: %s" % e)

  def onSave(self):
    if not self.exploration.is_dirty:
      return True

    if self.exploration.filename is None:
      self.onSaveAs()
    else:
      self.exploration.Save(self.exploration.filename)
      self.exploration.is_dirty = False

    if self.exploration.filename is not None:
      self.view.ui.statusbar.showMessage("Exploration saved at: %s" %
                                         self.exploration.filename)
      self._MarkExplorationAsSaved()

  def onSaveAs(self):
    filename = self._GetExplorationFileFromUser(is_open=False)
    if filename:
      try:
        outfilename = filename + ".explo"
        self.exploration.Save(filename=outfilename)
        self.exploration.filename = outfilename
        self._MarkExplorationAsSaved()
        self.exploration.is_dirty = False
      except IOError as e:
        raise ("Invalid exploration file: %s" % e)

  def onAddNewDatasourceDialog(self):
    dialog = AddNewDataSourceDialog(parent=None,
                                    main_presenter=self)
    dialog.exec_()

  def onAddNewTableDialog(self):
    dialog = AddNewTableDialog(parent=None,
                               main_presenter=self)
    dialog.exec_()

  def OnAddNewDataSource(self, datasource):
    self.exploration.AddDataSource(datasource)
    self._ResetTreeModel()

  def OnAddNewTable(self, table):
    self.exploration.AddTable(table)
    self._ResetTreeModel()

  def _ResetTreeModel(self):
    self.explorationtreemodel.reset()
    self.view.ui.treeView.update()

  def _GetExplorationFileFromUser(self, is_open=True, directory=''):
    if is_open:
      call = QFileDialog.getOpenFileName
    else:
      call = QFileDialog.getSaveFileName

    return call(
      caption="Choose an exploration file...",
      filter="Exploration files(*.explo);; All files (*.*);;",
      directory=directory,
      options=QFileDialog.Option)

  def _MarkExplorationAsSaved(self):
    pass

  def onTreeDoubleclick(self, index):
    print "(%d, %d) doubleclicked" % (index.row(), index.column())
    treenode = index.internalPointer()
    table = treenode.table
    self.view.ui.statusbar.showMessage("Loading table \"%s\"." %
                                       table.name)
    new_table_view = tableview_presenter.TableViewPresenter(
      exploration=self.exploration,
      table=table,
      parent=self.view)
    #self.presenters.append(new_table_view)
    #self.connect(new_table_view.view,
    #             SIGNAL("destroyed"),
    #             self.ontableViewClose)
    print "exitting onTreeDoubleClick"

  def ontableViewClose(self, view):
    print "ontableViewClose"
    for presenter in self.presenters:
      if presenter.view == view:
        self.presenters.remove(presenter)
        break


class AddNewDataSourceDialog(QDialog):
  # TODO(nop): This is wrong! We're doing MPV, not MVC
  def __init__(self, parent=None, main_presenter=None):
    super(AddNewDataSourceDialog, self).__init__(parent)
    self.presenter = main_presenter
    self.setAttribute(Qt.WA_DeleteOnClose)
    sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    self.setSizePolicy(sizePolicy)
    self.vboxLayout = QVBoxLayout()
    self.setLayout(self.vboxLayout)
    self.comboBox = QComboBox()
    self.comboBox.addItem(QString(''))
    self._SetupSources(self.comboBox)
    self.connect(self.comboBox, SIGNAL("currentIndexChanged(QString)"), self.updateSourceConfig)
    self.vboxLayout.addWidget(self.comboBox)
    self.nameInputWidget = QWidget()
    self.nameInputGrid = QGridLayout()
    self.nameInputWidget.setLayout(self.nameInputGrid)
    self.nameInputLabel = QLabel('Name')
    self.nameInputText = QLineEdit()
    self.nameInputGrid.addWidget(self.nameInputLabel, 0, 0)
    self.nameInputGrid.addWidget(self.nameInputText, 0, 1)
    self.vboxLayout.addWidget(self.nameInputWidget)
    self.dataSourceLayout = QGridLayout()
    self.dataSourceWidget = QFrame()
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
    self.connect(self.applyButton, SIGNAL('clicked()'), self.OnAddDataSource)
    self.connect(self.quitButton, SIGNAL('clicked()'), self.close)
    self.setWindowTitle("Add data source")

  def _SetupSources(self, combobox):
    for cls in sorted(model.DataSource.classes):
        if cls != model.DataSource.__name__:
            self.comboBox.addItem(QString(cls), QVariant())

  def updateSourceConfig(self, datasource_name):
    # delete first
    sip.delete(self.dataSourceWidget)
    self.dataSourceLayout = QGridLayout()
    self.dataSourceWidget = QFrame()
    self.dataSourceWidget.setLayout(self.dataSourceLayout)
    self.vboxLayout.insertWidget(1, self.dataSourceWidget)
    try:
      self.input_source = model.DataSource.classes[str(datasource_name)](
        name=self.nameInputText.text())
      print len(self.input_source.parameters)
      self._DrawConfigOptions(self.input_source,
                              self.dataSourceWidget,
                              self.dataSourceLayout)
    except KeyError, e:
      print e
    except AttributeError, e:
      print e
      label = QLabel("Error configuring datasource.")
      label.setStyleSheet("QLabel { color: red; font-weight: bold }")
      self.dataSourceLayout.addWidget(label)

  def _DrawConfigOptions(self, input_source, widget, layout):
    self.current_config_options = {}
    for (row, param_name) in enumerate(input_source.valid_parameters):
      param = input_source.valid_parameters.get(param_name)
      if not param:
        raise ValueError("Invalid parameter '%s'" % param_name)
      if not issubclass(param, datatypes.DataType):
        label = QLabel("Unknown parameter %s (%s)" %
                       (param_name, param.__class__.__name__))
        label.setStyleSheet("QLabel { color: red; font-weight: bold }")
        layout.addWidget(label)
      else:
        self.current_config_options[param_name] = param()
        self.current_config_options[param_name].RenderQtForm(layout,
                                                             name=param_name,
                                                             row=row)

  def OnAddDataSource(self):
    for name, value in self.input_source.valid_parameters.items():
      try:
        value = self.current_config_options[name]
        value.SetValueFromQt()
        try:
          if not value._gui_options['validator']():
            self.MarkAsInvalid(name)
        except KeyError:
          pass
        self.input_source.SetParameter(name=name, value=value)
      except ValueError:
        print "Parameter %s has an invalid value %s" % (name, value)
    self.close()
    self.presenter.OnAddNewDataSource(self.input_source)

  def MarkAsInvalid(self, name):
    self.current_config_options[name].label.setText(
      '<font color="red">'+self.current_config_options[name].label.text+'</font>')


class AddNewTableDialog(AddNewDataSourceDialog):
  def _SetupSources(self, combobox):
    for cls in sorted(model.Table.classes):
        if cls != model.Table.__name__:
            self.comboBox.addItem(QString(cls), QVariant())

  def OnAddDataSource(self):
    errors = 0
    for name, value in self.current_config_options.items():
      print "Going with %s (%s)" % (name, value)
      try:
        value.SetValueFromQt()
        try:
          print "Has validator? %s" % ('validator' in value._gui_options)
          print value._gui_options['validator']
          if not value._gui_options['validator']():
            print "does not validate"
            self.MarkParameterAsInvalid(name)
            errors += 1
            continue
        except (KeyError, TypeError), e:
          continue
        self.input_source.SetParameter(name=name, value=value)
      except (ValueError), e:
        self.MarkParameterAsInvalid(name)
        errors += 1
        print "Parameter %s has an invalid value %s (%s)" % (name, value, e)

    print "Errors: %d" % errors
    if not errors:
      self.close()
      self.presenter.OnAddNewTable(self.input_source)

  def MarkParameterAsInvalid(self, name):
    # TODO(parki): Do this better. This is awful
    self.current_config_options[name].label.setText(
      '<font color="red">'+self.current_config_options[name].label.text()+'</font>')

  def updateSourceConfig(self, datasource_name):
    # delete first
    sip.delete(self.dataSourceWidget)
    self.dataSourceLayout = QGridLayout()
    self.dataSourceWidget = QFrame()
    self.dataSourceWidget.setLayout(self.dataSourceLayout)
    self.vboxLayout.insertWidget(1, self.dataSourceWidget)
    try:
      self.input_source = model.Table.classes[str(datasource_name)]()
      print len(self.input_source.parameters)
      self._DrawConfigOptions(self.input_source,
                              self.dataSourceWidget,
                              self.dataSourceLayout)
    except KeyError, e:
      print e
    except AttributeError, e:
      label = QLabel("Error configuring datasource.")
      label.setStyleSheet("QLabel { color: red; font-weight: bold }")
      self.dataSourceLayout.addWidget(label)


class TreeNode(object):
  def __init__(self, parent, row):
    self.parent = parent
    self.row = row

  @property
  def subnodes(self):
    raise NotImplementedError()

class TreeModel(QAbstractItemModel):
  def __init__(self):
    QAbstractItemModel.__init__(self)
    self._root_nodes = self._GetRootNodes()

  def _GetRootNodes(self):
    raise NotImplementedError()

  def index(self, row, column, parent):
    if (row < 0 or column < 0 or row >= self.rowCount(parent)
        or column >= self.columnCount(parent)):
      return QtCore.QModelIndex()
    if not parent.isValid():
      return self.createIndex(row, column, self._root_nodes[row])
    parentNode = parent.internalPointer()
    return self.createIndex(row, column, parentNode.subnodes[row])

  def parent(self, index):
    if not index.isValid():
      return QModelIndex()
    node = index.internalPointer()
    if node.parent is None:
      return QModelIndex()
    else:
      return self.createIndex(node.parent.row, 0, node.parent)

  def reset(self):
    self._root_nodes = self._GetRootNodes()
    QAbstractItemModel.reset(self)

  def rowCount(self, parent):
    if not parent.isValid():
      return len(self._root_nodes)
    if parent.column() > 0:
      return 0
    node = parent.internalPointer()
    return len(node.subnodes)


class MetaTableListNode(TreeNode):
  def __init__(self, exploration=None, parent=None, row=None):
    self.name = "MetaTables"
    self.exploration = exploration
    self.metatables = [MetaTableNode(metatable=metatable, parent=self, row=i)
                       for i, metatable in enumerate(self.exploration.metatables)]
    super(MetaTableListNode, self).__init__(parent, row)

  @property
  def subnodes(self):
    return self.metatables


class TableListNode(TreeNode):
  def __init__(self, exploration=None, parent=None, row=None):
    self.name = "Tables"
    self.exploration = exploration
    self.tables = [TableNode(table=table, parent=self, row=i)
                   for i, table in enumerate(self.exploration.tables)]
    super(TableListNode, self).__init__(parent, row)

  @property
  def subnodes(self):
    return self.tables


class DataSourceListNode(TreeNode):
  def __init__(self, exploration=None, parent=None, row=None):
    self.name = "DataSources"
    self.exploration = exploration
    self.datasources = [DataSourceNode(datasource=datasource, parent=self, row=i)
                        for i, datasource in enumerate(self.exploration.datasources)]
    super(DataSourceListNode, self).__init__(parent, row)

  @property
  def subnodes(self):
    return self.datasources


class TableNode(TreeNode):
  def __init__(self, table=None, parent=None, row=None):
    self.table = table
    self.datasources = [DataSourceNode(datasource=self.table.datasource,
                                       parent=self,
                                       row=0)]
    #return [DataSourceNode(datasource=datasource, parent=self, row=i)
    #        for i, datasource in enumerate(self.table.datasources)]
    super(TableNode, self).__init__(parent, row)

  @property
  def subnodes(self):
    return self.datasources


class MetaTableNode(TreeNode):
  def __init__(self, metatable=None, parent=None, row=None):
    self.table = metatable
    self.tables = [TableNode(table=table, parent=self, row=i)
                   for i, table in enumerate(self.table.tables)]
    super(MetaTableNode, self).__init__(parent, row)

  @property
  def subnodes(self):
    return self.tables


class DataSourceNode(TreeNode):
  def __init__(self, datasource=None, parent=None, row=None):
    self.datasource = datasource
    super(DataSourceNode, self).__init__(parent, row)

  @property
  def subnodes(self):
    return []


class ExplorationModel(TreeModel):
  def __init__(self, exploration=None):
    self.exploration = exploration
    super(ExplorationModel, self).__init__()

  def headerData(self, section, orientation, role):
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
      return "Name"
    return None

  def _GetRootNodes(self):
    #return [MetaTableNode(metatable=metatable, parent=None, row=i)
    #        for i, metatable in enumerate(self.exploration.metatables)]
    return [DataSourceListNode(exploration=self.exploration, row=0),
            TableListNode(exploration=self.exploration, row=1),
            MetaTableListNode(exploration=self.exploration, row=2)]

  def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
    return 1

  def data(self, index, role=None):
    if not index.isValid():
      return None
    if role != Qt.DisplayRole:
      return None
    node = index.internalPointer()
    if isinstance(node, MetaTableNode):
      return QVariant(node.table.name)
    elif isinstance(node, TableNode):
      return QVariant(node.table.name)
    elif isinstance(node, DataSourceNode):
      return QVariant(node.datasource.name)
    elif (isinstance(node, DataSourceListNode) or
          isinstance(node, TableListNode) or
          isinstance(node, MetaTableListNode)):
      return QVariant(node.name)
    else:
      print "Unknown node %s" % node.__class__
    return QVariant()
