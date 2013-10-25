#! /usr/bin/python

import ConfigParser
import functools
import json
import logging

from logally.lib import datatypes
from logally.lib import index
from logally.lib import utils


### EXCEPTIONS
class Error(BaseException):
  pass


class TableNotOpened(Error):
  pass


class TableNotIndexedError(Error):
  pass


### MAIN CLASSES
class DataSource(object):
  __metaclass__ = utils.MetaclassRegistry

  valid_parameters = dict()

  def __init__(self, name=None, uuid=None):
    self.name = name
    # A dictionary of parameters
    self.parameters = dict()
    self.id = uuid or utils.UUID()

  def Open(self):
    """Prepares the DataSource to be used."""
    raise NotImplemented

  def SetParameter(self, name=None, value=None):
    if name not in self.valid_parameters.keys():
      raise ValueError("Parameter unknown")
    else:
      self.parameters[name] = value

  def Read(self, size=None):
    """Reads size data units from the data source. The data unit depends on
       each datasource."""

  def __str__(self):
    return "%s(%s)" % (self.__class__.__name__,
           ', '.join(['%s=%s' % (k, v) for k, v in self.parameters.items()]))

  def __repr__(self):
    return str(self)


class Row(object):
  def __init__(self, cells=None, table=None):
    if not table:
      raise ValueError("Invalid table.")
    if len(cells) != table.column_count:
      raise ValueError("Invalid number of cells.")
    self._cells = cells or []
    self._cells_by_name = dict()
    # TODO(parki): Revisit _cells_by_name
    for cell in cells:
      self._cells_by_name[cell.name] = cell

  def __getitem__(self, item):
    try:
      return self._cells[item]
    except TypeError:
      # Maybe item is actually not an index...
      # act like a dict and find it via column name...
      return self._cells_by_name[item]


class Column(utils.Sender):
  """Represents a named column with a type. Does not contain actual data."""

  def __init__(self, name=None, datatype=datatypes.NoType):
    super(Column, self).__init__()
    # The name of this column
    self.name = name
    # The DataType of this column. Ignored for now
    if datatype is None or not issubclass(datatype, datatypes.DataType):
      raise ValueError("Type %s is invalid." % datatype)
    self.type = datatype

  def SerializeToDict(self):
    data = {
      "name": self.name,
      "type": self.type.__name__
    }
    return data

  def SerializeToString(self):
    return json.dumps(self.SerializeToDict())


@functools.total_ordering
class Cell(object):
  def __init__(self, value=None, column=None):
    self.value = value
    self.name = column.name

  def __lt__(self, other):
    return self.value < other.value

  def __eq__(self, other):
    return self.value == other.value

  def __str__(self):
    return "Cell(%s)" % self.value


class Table(utils.Sender):
  """Contains a set of columns and returns rows which are lists of cells.

  A table must present rows ordered.to the order column.
  """

  __metaclass__ = utils.MetaclassRegistry

  valid_parameters = dict()

  def __init__(self, name=None, datasource=None, uuid=None):
    super(Table, self).__init__()
    self.row_count = 0
    self.name = name
    self.is_open = False
    self.is_indexed = False
    self.parameters = dict()
    self.datasource = datasource
    self.uuid = uuid or utils.UUID()
    self._columns = []
    self._order_column = None

  @property
  def column_count(self):
    """The number of columns for this table."""

    return len(self.columns)

  def Open(self):
    """Prepares the Table to be used.

    Must set self.is_open to True once the table is open.
    """
    if self.datasource:
      self.datasource.Open()
    self.is_open = True

  def Close(self):
    """Closes the current table."""

  def __del__(self):
    self.Close()

  def Cell(self, row_index=0, column_index=0):
    """Returns the cell at (row_index, column_index).

    This method is meant to be overriden by Table plugins.
    """

  def Rows(self, start=0):
    """A generator of rows.

    Rows are simply lists of values."""
    if not self.is_open:
      raise TableNotOpened()

    for row in range(start, self.row_count):
      cells = []
      for i in range(self.column_count):
        cell = self.Cell(row_index=row, column_index=i)
        cells.append(cell)
      yield Row(cells=cells, table=self)

  def _ValidateColumn(self, column=None):
    if column is None or column.type is None or column.name is None:
      raise ValueError("Invalid column")
    for c in self.columns:
      if c.name == column.name:
        raise ValueError("Invalid column: Name %s already exists." %
                         column.name)
    return True

  def InsertColumn(self, column=None, index=None):
    """Inserts the column to the end."""
    if index is None:
      raise IndexError("No index specified.")
    self._ValidateColumn(column)
    try:
      self._columns.insert(index, column)
    except IndexError:
      self._columns.append(column)
    return True

  def AppendColumn(self, column=None):
    """Adds a column to the end."""
    self._ValidateColumn(column)
    return self.InsertColumn(column, index=self.column_count)

  def RemoveColumn(self, column=None):
    """Deletes the column from the list of columns."""
    if column in self._columns:
      self._columns.remove(column)
      if column == self._order_column:
        old_order_column = self._order_column
        self._order_column = None
        self.signal("orderColumnChanged",
                    old_order_column,
                    self._order_column)
      return True
    return False

  def MoveColumn(self, column=None, index=None):
    """Moves the column to position index."""

    if column in self._columns:
      self.RemoveColumn(column=column)
      self.InsertColumn(column=column, index=index)
      return True
    return False

  def ColumnIndex(self, column=None):
    """Returns the index at which the column is."""
    return self._columns.index(column)

  def ColumnByName(self, name=None):
    """Returns the column by its name."""
    for column in self.columns:
      if column.name == name:
        return column
    return None

  def ColumnsOf(self, datatype=None):
    """Returns a list of columns of the given datatype."""

    if datatype is not None:
      return [column for column in self.columns
              if issubclass(column.type, datatype)]
    else:
      return self.columns

  def ColumnAt(self, index=0):
    """Returns the column at the given index."""

    if index < 0 or index >= self.column_count:
      raise IndexError("Column %d does not exist." % index)
    return self.columns[index]

  @property
  def columns(self):
    """Returns an ordered list of Column."""
    return self._columns

  def OrderColumn(self):
    self._HasOrderColumn()
    return self._order_column

  def _HasOrderColumn(self):
    if self._order_column is None:
      raise ValueError("No order column set!")

  def SetOrderColumn(self, index=None):
    """Sets the current order column to column_index.

    Signals:
        orderColumnChanged(oldcolumn, newcolumn)
            When the order column has changed.
    """

    order_column = self.ColumnAt(index=index)
    # This is so wrong... but a fair decision for now...
    if not issubclass(order_column.type, datatypes.DatetimeType):
      raise ValueError("Column %d is not a timestamp.")
    old_order_column = self._order_column
    self._order_column = order_column
    self.signal("orderColumnChanged", old_order_column, self._order_column)

  def SetParameter(self, name=None, value=None):
    """Sets one of the parameters valid for the table.

    Must be one in self.valid_parameters.
    """
    if name not in self.valid_parameters:
      raise ValueError("Parameter unknown.")
    if not isinstance(value, self.valid_parameters.get(name)):
      raise ValueError(
        "Value is not of type %s." % self.valid_parameters.get(name))
    self.parameters[name] = value

  def SetDataSource(self, datasource=None):
    """Sets the datasource for this table."""
    self.datasource = datasource
    self.signal("dataSourceChanged")

  def SerializeToDict(self):
    data = {
      "name": self.name,
      "type": self.__class__.__name__,
      "uuid": self.uuid.hex,
      "columns": [],
      "order": self._order_column.id.hex,
      "parameters": {}
    }

    for column in self.columns:
      data["columns"].append(column.SerializeToDict())

    for parameter, value in self.parameters.items():
      data["parameters"].set(parameter, value)
    return data

  def SerializeToString(self):
    return json.dumps(self.SerializeToDict())

  def CreateIndex(self, exploration):
    """Generates an index for the current table."""


class MetaColumn(Column):
  """A column that references the contents of columns in other tables."""

  def __init__(self, name=None, datatype=None):
    super(MetaColumn, self).__init__(name=name, datatype=datatype)
    self.references = dict()

  def ColumnForTable(self, table):
    return self.references.get(table)

  def SetReference(self, table=None, column=None):
    """Adds a reference to the column in the table."""

    if column not in table.columns:
      raise ValueError("Column %s not found in table %s." % (column.name,
                                                             table.name))
    self.references[table] = column

  def RemoveReference(self, table=None):
    """Removes the reference to this table."""
    del self.references[table]

  def Unserialize(self):
    pass

  def SerializeToDict(self):
    data = {
      "name": self.name,
      "type": self.type.__name__,
      "references": {},
    }

    for reference, column in self.references.items():
      data["references"].set(reference.id.hex, column.name)

  def SerializeToString(self):
    return json.dumps(self.SerializeToDict())


class MetaTable(Table):
  """A table backed by one or more tables.

  Its rows return columns that are a mix of columns from different tables.
  """

  def __init__(self, uuid=None, name=None, columns=None, tables=None,
               metaindex=None):
    super(MetaTable, self).__init__(name=name, uuid=uuid)
    self.name = name
    self.uuid = uuid or utils.random_uuid()

    try:
      self._tables = set(list(tables))
    except TypeError:
      self._tables = set()

    _columns = columns or []

    self._is_indexed = False
    self._metaindex = metaindex
    if isinstance(self._metaindex, index.MetaTableIndex):
      self._is_indexed = True

    for column in _columns:
      self.AppendColumn(column=column)

  @property
  def tables(self):
    return list(self._tables)

  @property
  def row_count(self):
    total_count = 0
    for table in self.tables:
      total_count += table.row_count
    return total_count

  @row_count.setter
  def row_count(self, value):
    pass

  def Open(self):
    if not self._is_indexed:
      raise TableNotIndexedError()

    for table in self.tables:
      table.Open()
    self.is_open = True

  def SetIndex(self, metaindex=None):
    if not isinstance(metaindex, index.MetaTableIndex):
      raise ValueError()
    self._metaindex = metaindex
    self._is_indexed = True

  def Cell(self, row_index=0, column_index=0):
    """Returns the cell at (row_index, column_index).

    Raises:
      KeyError: When there's no reference in the metacolumn at column_index to
      the table that holds the Cell data.
    """
    if not self._is_indexed:
      raise TableNotIndexedError()
    if column_index < 0 or column_index >= self.column_count:
      raise IndexError()
    # Find the metacolumn at the given index
    metacolumn = self.ColumnAt(index=column_index)
    table_uuid, table_row_index = self._metaindex.GetRow(
      row_index=row_index)
    table = self._TableById(uuid=table_uuid)
    # Obtain the index of the column_index of the table that holds data for the
    # metacolumn.
    try:
      table_column_index = table.ColumnIndex(metacolumn.ColumnForTable(table))
    except ValueError:
      # When no reference to the table column is found.
      return None
    return table.Cell(column_index=table_column_index, row_index=table_row_index)

  def _TableById(self, uuid=None):
    """Returns the table with uuid uuid associated with this MetaTable.

    Returns:
      An instance of the Table with this uuid, or None if not found.
    """

    for table in self._tables:
      if table.uuid == uuid:
        return table
    raise ValueError("No table with uuid %s found" % uuid)

  def InsertColumn(self, column=None, index=None):
    self._ValidateColumn(column)
    res = super(MetaTable, self).InsertColumn(column=column, index=index)
    if res:
      self._AddTablesForColumn(column=column)
      return True
    return False

  def AppendColumn(self, column=None):
    self._ValidateColumn(column)
    res = super(MetaTable, self).AppendColumn(column=column)
    if res:
      self._AddTablesForColumn(column=column)
      return True
    return False

  def RemoveColumn(self, column=None):
    self._ValidateColumn(column)
    res = super(MetaTable, self).AppendColumn(column=column)
    if res:
      self._RemoveTablesForColumn(column=column)
      return True
    return False

  def _ValidateColumn(self, column=None):
    if super(MetaTable, self)._ValidateColumn(column=column):
      return isinstance(column, MetaColumn)
    raise ValueError("Invalid column.")

  def _AddTablesForColumn(self, column=None):
    for table in column.references:
      self._tables.add(table)

  def _RemoveTablesForColumn(self, column):
    tables_in_column = set()

    for table in column.references:
      tables_in_column.add(table)

    tables_in_other_columns = set()
    for current_column in self.columns:
      if current_column == column:
        continue
      for table in current_column.references:
        tables_in_other_columns.add(table)

    for table in tables_in_column.difference(tables_in_other_columns):
      self._tables.remove(table)


class Transform(object):
  """Base class for transforms."""
  __metaclass__ = utils.MetaclassRegistry

  input_types = []
  output_types = []
  description = """Transforms should have a description. Otherwise you'll get
    this silly description: Chicken. Banana. Sneaky Pirate. Gopher. Fig."""

  def Transform(self, value):
    raise NotImplemented

  @classmethod
  def TransformsFor(cls, input_type):
    valid_transforms = []
    for name, transform_cls in cls.classes.items():
      # Skip the base classes
      if transform_cls == cls:
        continue
      if input_type in transform_cls.input_types:
        valid_transforms.append(transform_cls)
    return valid_transforms


class Exploration(object):
  """Represents an exploration session.

  It stores a set of datasources, tables and views.
  """

  def __init__(self, name=None, is_dirty=True):
    self.name = name
    self.metatables = []
    self.datasources = []
    self.tables = []
    self.filename = None
    self.is_dirty = is_dirty
    self.base_directory = None

  @classmethod
  def Load(cls, filename=None):
    if not filename:
      raise ValueError("No filename specified.")
    parser = ConfigParser.SafeConfigParser()
    with open(filename, "r") as fd:
      parser.readfp(fd)

    exploration = cls(name="Test exploration", is_dirty=False)
    exploration.filename = filename

    datasources = set()
    tables = set()
    metatables = set()
    for section in parser.sections():
      if section.beginswith("datasource:"):
        datasource = cls._LoadDataSource(parser=parser, name=section)
        datasources.add(datasource)
      elif section.beginswith("table:"):
        table = cls._LoadTable(parser=parser, name=section)
        tables.add(table)
      elif section.beginswith("metatable:"):
        metatable = cls._LoadMetaTable(parser=parser, name=section)
        metatables.add(metatable)
      else:
        logging.warn("Unknown section %s", section)
        continue
    exploration.datasources = list(datasources)
    exploration.tables = list(tables)
    exploration.metatables = list(metatables)

  @classmethod
  def _LoadDataSource(cls, parser=None, name=''):
    datasource, params = cls._LoadResource(parser=parser, name=name,
                                           base_type=DataSource)

    for key, value in params.items():
      datasource.SetParameter(key, value)

  @classmethod
  def _LoadTable(cls, parser=None, name=''):
    return cls._LoadResource(parser=parser, name=name,
                             base_type=Table)

  @classmethod
  def _LoadMetaTable(cls, parser=None, name=''):
    return cls._LoadResource(parser=parser, name=name,
                             base_type=MetaTable)

  @classmethod
  def _LoadResource(cls, parser=None, name='', base_type=None):
    _type = None
    _name = None
    _id = None
    parameters = {}

    for parameter, value in parser.items(name):
      if parameter == "type":
        _type = value
      elif parameter == "name":
        _name = value
      elif parameter == "uuid":
        _id = value
      else:
        parameters[parameter] = value

    if not _type:
      raise ValueError("Unknown Data Source %s type specified." % _type)

    klass = base_type.classes.get(_type, None)
    if not klass:
      raise ValueError("Specified data source type %s unavailable." %
                       _type)

    instance = klass(name=_name, id=_id)
    for parameter, value in parameters.items():
      instance.SetParameter(parameter, value)
    return instance

  def Save(self):
    if not self.filename:
      raise ValueError("No filename specified.")

    parser = ConfigParser.SafeConfigParser()
    for i, datasource in enumerate(self.datasources):
      section = 'datasource:%d' % i
      parser.add_section(section)
      parser.set(section, "uuid", str(datasource.id))
      for name, value in datasource.parameters.iteritems():
        parser.set(section, name, value)

    for i, table in enumerate(self.tables):
      section = 'table:%d' % i
      parser.add_section(section)
      parser.set(section, "uuid", str(table.uuid))
      for name, value in table.parameters.iteritems():
        parser.set(section, name, value)

    for i, metatable in enumerate(self.metatables):
      section = 'metatable:%d' % i
      parser.add_section(section)
      parser.set(section, "uuid", str(metatable.uuid))
      for name, value in metatable.parameters.iteritems():
        parser.set(section, name, value)
      table_ids = [str(table.uuid) for table in metatable.tables]
      parser.set(section, "tables", ','.join(table_ids))
    with open(self.filename, "w") as fd:
      parser.write(fd)

  def AddMetaTable(self, metatable=None):
    self.metatables.append(metatable)

  def AddTable(self, table=None):
    self.tables.append(table)

  def AddDataSource(self, datasource=None):
    self.datasources.append(datasource)