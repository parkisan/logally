#! /usr/bin/python
from twisted.persisted.crefutil import _DictKeyAndValue

import cStringIO
import unittest

from logally import model
from logally.lib import datatypes
from logally.lib import index


class FakeDataSource(model.DataSource):
  """A fake data source."""

  def __init__(self, name=None, uuid=None):
    super(FakeDataSource, self).__init__(name=name, uuid=uuid)

  def Open(self):
    return True


class FakeTable(model.Table):
  """A fake data source that returns the specified set of row data."""

  def __init__(self, name=None, uuid=None, rows=None, columns=None):
    super(FakeTable, self).__init__(name=name, uuid=uuid)
    self._rows = rows or []
    self.row_count = len(self._rows)
    self._columns = columns or []
    self.is_open = True

  def Cell(self, row_index=0, column_index=0):
    try:
      return model.Cell(value=self._rows[row_index][column_index],
                        column=self.ColumnAt(index=column_index))
    except IndexError:
      raise ValueError("Invalid cell (%ld, %ld)" % (row_index, column_index))

  def Rows(self, start=0):
    for row in self._rows[start:]:
      yield row


class TestBaseModels(unittest.TestCase):
  class MyDataSource(model.DataSource):
    valid_parameters = {"param1": None}


  def setUp(self):
    self.datasource1 = self.MyDataSource(name="test1")
    self.col1 = model.Column(name="time", datatype=datatypes.DatetimeType)
    self.table1 = model.Table(name="table1")
    self.cell1 = model.Cell(value="Test cell", column=self.col1)
    self.fd = cStringIO.StringIO()
    self.table_definition = {
      "table1": {
        "rows": [
          [50, "row10"],
          [56, "row11"],
          [58, "row12"],
          [59, "row13"]
        ]
      },
      "table2": {
        "rows": [
          [1, "row20"],
          [54, "row21"],
          [56, "row22"],
          [60, "row23"]
        ],
      },
      "table3": {
        "rows": [],
      },
    }
    self.columns = [model.Column(name="date", datatype=datatypes.DatetimeType),
                    model.Column(name="msg", datatype=datatypes.NoType),
    ]

    self.calculated_total_rows = 0
    self.tables = []
    for (name, table_def) in self.table_definition.items():
      table = FakeTable(name=name,
                        rows=table_def["rows"],
                        columns=self.columns)
      self.calculated_total_rows += len(table_def["rows"])
      table.SetOrderColumn(index=0)
      table.Open()
      self.tables.append(table)

    self.metatable = model.MetaTable(name="metatable")
    self.date_metacolumn = model.MetaColumn(name="date",
                                            datatype=datatypes.DatetimeType)
    self.num_metacolumn = model.MetaColumn(name="num",
                                           datatype=datatypes.NoType)
    for table in self.tables:
      self.date_metacolumn.SetReference(table, column=self.columns[0])
      self.num_metacolumn.SetReference(table, column=self.columns[1])

    self.metatable.AppendColumn(self.date_metacolumn)
    self.metatable.AppendColumn(self.num_metacolumn)

    self.metaindex = index.MetaTableIndex()
    self.metaindex.Save(file_obj=self.fd, metatable=self.metatable)
    self.fd.seek(0)
    self.metaindex.Load(file_obj=self.fd)
    self.metatable.SetIndex(self.metaindex)

  def testDataSourceInit(self):
    self.assertEqual(self.datasource1.name, "test1")

  def testDataSourceParameters(self):
    self.assertRaises(ValueError,
                      self.datasource1.SetParameter,
                      name="unk_param",
                      value=2)
    self.datasource1.SetParameter(name="param1", value=2)
    self.assertEqual(self.datasource1.parameters["param1"], 2)

  def testColumnInit(self):
    self.assertEqual(self.col1.name, "time")

  def testColumnOps(self):
    # Initial column count
    self.assertEqual(0, self.table1.column_count)
    # Append a column
    self.table1.AppendColumn(column=self.col1)
    self.assertEqual(1, self.table1.column_count)
    self.assertEqual([self.col1], self.table1.columns)
    # Try to append an invalid column
    self.assertRaises(ValueError, self.table1.AppendColumn)
    # Try to append a column with the same name
    self.assertRaises(ValueError, self.table1.AppendColumn,
                      model.Column(name=self.col1.name))
    # Insert a column at the start
    new_column = model.Column(name="new column",
                              datatype=datatypes.UTF8StringType)
    self.table1.InsertColumn(column=new_column, index=0)
    self.assertEqual(2, self.table1.column_count)
    self.assertListEqual([new_column, self.col1], self.table1.columns)
    # Remove it
    res = self.table1.RemoveColumn(column=new_column)
    self.assertEqual(1, self.table1.column_count)
    self.assertListEqual([self.col1], self.table1.columns)
    self.assertEqual(res, True)
    # Put way past the last column
    res = self.table1.InsertColumn(column=new_column, index=2000)
    self.assertEqual(2, self.table1.column_count)
    self.assertListEqual([self.col1, new_column], self.table1.columns)
    self.assertEqual(res, True)
    # Move a fake column
    res = self.table1.MoveColumn(column="boo", index=20)
    self.assertEqual(2, self.table1.column_count)
    self.assertListEqual([self.col1, new_column], self.table1.columns)
    self.assertEqual(res, False)
    # Swap columns...
    res = self.table1.MoveColumn(column=self.col1, index=1)
    self.assertEqual(2, self.table1.column_count)
    self.assertListEqual([new_column, self.col1], self.table1.columns)
    self.assertEqual(res, True)
    # Move new_column to position 0... that is... do nothing
    res = self.table1.MoveColumn(column=new_column, index=0)
    self.assertEqual(2, self.table1.column_count)
    self.assertListEqual([new_column, self.col1], self.table1.columns)
    self.assertEqual(res, True)
    # Find index for each column
    self.assertEqual(0, self.table1.ColumnIndex(column=new_column))
    self.assertEqual(1, self.table1.ColumnIndex(column=self.col1))
    # Find columns by index
    self.assertEqual(new_column, self.table1.ColumnAt(index=0))
    self.assertEqual(self.col1, self.table1.ColumnAt(index=1))
    # Find columns by type
    self.assertListEqual(
      [],
      self.table1.ColumnsOf(datatype=datatypes.FilenameType))
    columns = self.table1.ColumnsOf(datatype=datatypes.UTF8StringType)
    self.assertListEqual([new_column], columns)
    columns = self.table1.ColumnsOf(datatype=datatypes.DatetimeType)
    self.assertListEqual([self.col1], columns)
    # Set order column to a valid column
    # Try to set a non-existent column as the order column
    self.assertRaises(IndexError,
                      self.table1.SetOrderColumn, index=200)
    # Try to set a non datetime column as the order column
    self.assertRaises(ValueError,
                      self.table1.SetOrderColumn, index=0)
    # Now set a proper one
    self.table1.SetOrderColumn(index=1)
    self.assertEqual(
      self.table1._order_column,
      self.table1.ColumnAt(index=1))


  def testRowInit(self):
    # We make our table have 1 column so we can test row
    self.table1.AppendColumn(self.col1)
    self.row1 = model.Row(cells=[self.cell1], table=self.table1)
    self.assertRaises(ValueError, model.Row, cells=[], table=self.table1)
    self.assertRaises(ValueError, model.Row, cells=self.row1)
    self.table1.RemoveColumn(column=self.col1)
    # Try row indexing by integer
    self.assertRaises(IndexError, self.row1.__getitem__, 12)
    self.assertRaises(IndexError, self.row1.__getitem__, -2)
    self.assertEqual(self.row1[0], self.cell1)
    # Try row indexing by column name
    self.assertEqual(self.row1[self.col1.name], self.cell1)
    self.assertRaises(KeyError, self.row1.__getitem__, "unknown column")

  def testTableInit(self):
    self.assertEqual(self.table1.row_count, 0)
    self.assertEqual(self.table1.column_count, 0)
    self.assertEqual(self.table1.name, "table1")

  def testMetaColumn(self):
    table = FakeTable(name="test_table")
    column = model.Column(name="test_column")
    table.AppendColumn(column)
    metacolumn = model.MetaColumn(datatype=datatypes.NoType)
    metacolumn.SetReference(table, column=table.ColumnAt(0))
    metacolumn.RemoveReference(table)
    self.assertRaises(KeyError, metacolumn.RemoveReference, table)

  def testMetaTable(self):
    self.metatable.Open()
    date_values = [v[0].value for v in self.metatable.Rows()]
    self.assertEqual([1, 50, 54, 56, 56, 58, 59, 60], date_values)
    num_metacolumn = self.metatable.ColumnAt(1)
    # Let's remove a reference to the 2nd table
    #for table in list(num_metacolumn.references):
    #  num_metacolumn.RemoveReference(table)
    num_metacolumn.RemoveReference(self.tables[0])
    # Getting the cell (0,1) should return None as it points to the 2nd
    # table, 2nd column
    cell_0_1 = self.metatable.Cell(row_index=0, column_index=1)
    self.assertEqual(None, cell_0_1)


if __name__ == '__main__':
  unittest.main()
