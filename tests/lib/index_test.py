import cStringIO
import logging
import random
import unittest

from logally import model
from logally.lib import datatypes
from logally.lib import index
from logally.lib import utils
from tests import model_test


class TestMetaTableIndex(unittest.TestCase):
  def setUp(self):
    """Set up a fake metatable."""
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
      table = model_test.FakeTable(name=name,
                                   rows=table_def["rows"],
                                   columns=self.columns)
      self.calculated_total_rows += len(table_def["rows"])
      table.SetOrderColumn(index=0)
      logging.debug("Appending %s" % name)
      self.tables.append(table)

    self.metatable = model.MetaTable(name="metatable")
    self.metacolumn = model.MetaColumn(name="data",
                                       datatype=datatypes.DatetimeType)
    for table in self.tables:
      self.metacolumn.SetReference(table, column=self.columns[0])
    self.metatable.AppendColumn(self.metacolumn)

  def testStoreLoadMetaData(self):
    test_values = (
      (1, 1, 1),
      (256, pow(2, 16), 16)
    )
    for (tables, rows_x_table, uuid_size) in test_values:
      stored_index = index.MetaTableIndex(max_tables=tables,
                                          max_rows_per_table=rows_x_table,
                                          uuid_size=uuid_size)
      stored_index._StoreMetaData(file_obj=self.fd)
      blank_index = index.MetaTableIndex()
      # Load from the start
      self.fd.seek(0)
      metadata = blank_index._LoadMetaData(file_obj=self.fd)
      (_, blank_tables, blank_rows_x_table, blank_uuid_size) = metadata
      self.assertEqual(tables, blank_tables)
      self.assertEqual(rows_x_table, blank_rows_x_table)
      self.assertEqual(uuid_size, blank_uuid_size)
      # Reset the data
      self.fd.truncate(0)

  def testStoreLoadTables(self):
    test_sizes = [1, 48, 256, 1024, random.randint(1, pow(2, 16))]
    for size in test_sizes:
      # Quick way to create a large list of UUIDs without hogging
      # the RNG
      random_uuids = [utils.UUID(from_value="\x00" * 16)
                      for _ in range(size)]
      tables = [model.Table(name="table%s" % uuid.hex, uuid=uuid)
                for uuid in random_uuids]
      stored_index = index.MetaTableIndex(max_tables=len(tables),
                                          max_rows_per_table=12)
      for table in tables:
        stored_index.AddTable(table=table)

      stored_index._StoreTables(file_obj=self.fd)
      self.fd.seek(0)
      blank_index = index.MetaTableIndex(max_tables=len(tables),
                                         max_rows_per_table=12)
      metadata = (None, blank_index.max_tables,
                  blank_index.max_rows_per_table, blank_index.uuid_size)
      blank_index._LoadTables(file_obj=self.fd, metadata=metadata)
      uuids = [table.uuid.hex for table in tables]

      for uuid in blank_index.tables:
        self.assertNotEqual(uuid, None)
        self.assertTrue(uuid.hex in uuids)
      self.fd.truncate(0)

  def testStoreLoadData(self):
    metatable_index = index.MetaTableIndex(
      max_tables=len(self.metatable.tables),
      max_rows_per_table=pow(2, 32) - 1)

    total_rows = metatable_index._StoreData(metatable=self.metatable,
                                           file_obj=self.fd)
    self.assertEqual(self.calculated_total_rows, total_rows)
    logging.debug("Total of %ld rows.", total_rows)

  def testSaveLoad(self):
    initial_index = index.MetaTableIndex(
      max_tables=len(self.metatable.tables),
      max_rows_per_table=pow(2, 32) - 1)
    initial_index.Save(file_obj=self.fd, metatable=self.metatable)
    loaded_index = index.MetaTableIndex()
    self.fd.seek(0)
    #print self.fd.read().encode('hex')
    loaded_index.Load(file_obj=self.fd)
    self.assertEqual(loaded_index.max_tables, initial_index.max_tables)
    self.assertEqual(loaded_index.max_rows_per_table,
                     initial_index.max_rows_per_table)
    self.assertEqual(loaded_index.uuid_size, initial_index.uuid_size)
    initial_uuids = [uuid.hex for uuid in initial_index.tables]
    loaded_uuids = [uuid.hex for uuid in loaded_index.tables]
    self.assertListEqual(loaded_uuids, initial_uuids)
    uuid_to_index = map(lambda x: x.hex, loaded_index.tables)
    # Now validate the rows!
    rows = []
    for row_index in range(loaded_index.row_count):
      table_id, table_row = loaded_index.GetRow(row_index=row_index)
      table_index = uuid_to_index.index(table_id.hex)
      table_name = self.metatable.tables[table_index].name
      rows.append(self.table_definition[table_name]["rows"][table_row])

    ordered_column = map(lambda x: x[0], rows)
    self.assertListEqual(ordered_column, sorted(ordered_column))
    self.assertListEqual([1, 50, 54, 56, 56, 58, 59, 60], ordered_column)
