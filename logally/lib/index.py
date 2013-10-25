import bisect
import logging
import os
import struct

from logally.lib import utils

class Error(Exception):
  pass

class IndexNotLoadedError(Error):
  pass

class MetaTableIndex(object):
  """Creates an index that maps a metatable row to the row of a real table.

  Suitable for datasources that are immutable."""

  magic = "m\x37\xa1n\xdex\x00\x00"

  def __init__(self, max_tables=256, max_rows_per_table=pow(2, 32),
               uuid_size=16):
    self.file_obj = None
    self.max_tables = max_tables
    self.max_rows_per_table = max_rows_per_table
    self.uuid_size = uuid_size
    # Stores a list of UUIDs of the tables indexed in this index
    self.tables = []
    # References the file-like object where the index can be read from
    self.disk_index = None
    self.metadata_struct = struct.Struct(">8sQQQ")
    metadata = (self.magic, max_tables, max_rows_per_table, uuid_size)
    self._RegenerateStructures(metadata=metadata)
    # A cache to write the index data to disk in batches to not flood the
    # storage device with tiny I/O requests (good/bad decision?)
    self._out_cache = []
    self.row_count = 0

  def _CalcStructSize(self, size):
    _size_map = (
      (1, 'B'),
      (2, 'H'),
      (4, 'L'),
      (8, 'Q'))

    if size <= 0:
      raise ValueError("Invalid value %ld" % size)
    for bytes, struct_letter in _size_map:
      if size < pow(2, 8 * bytes):
        return struct_letter
    raise ValueError("%ld is too large." % size)

  def _RegenerateStructures(self, metadata=None):
    """Regenerates the base structures needed to perform calculations."""
    (_, max_tables, max_rows_per_table, uuid_size) = metadata
    max_tables_size = self._CalcStructSize(max_tables)
    table_struct_string = ">%ds" % uuid_size
    self.table_struct = struct.Struct(table_struct_string)
    max_rows_per_table_size = self._CalcStructSize(max_rows_per_table)
    row_struct_string = ">%c%c" % (max_tables_size,
                                   max_rows_per_table_size )
    self.row_struct = struct.Struct(row_struct_string)

  def Load(self, file_obj=None):
    """Loads the index structure and tables from file_obj."""
    self.file_obj = file_obj
    self.file_obj.seek(0)
    metadata = self._LoadMetaData(file_obj=self.file_obj)
    (magic, max_tables, max_rows_x_table, uuid_size) = metadata
    self.max_tables = max_tables
    self.max_rows_per_table = max_rows_x_table
    self.uuid_size = uuid_size
    # Discard the given data structures and generate new ones with the
    # new metadata
    self._RegenerateStructures(metadata=metadata)
    tables = self._LoadTables(file_obj=file_obj, metadata=metadata)
    self.tables = tables
    self.disk_index = file_obj

    self.file_obj.seek(0, os.SEEK_END)
    total_size = self.file_obj.tell()
    row_data_size = total_size - self.metadata_struct.size
    row_data_size -= self.table_struct.size * self.max_tables
    self.row_count = row_data_size / self.row_struct.size

  def _LoadMetaData(self, file_obj=None):
    """Loads and returns the metadata available in file_obj.

    Returns:
      (magic, max_tables, max_rows_x_table, uuid_size)
    """
    data = file_obj.read(self.metadata_struct.size)
    unpacked = self.metadata_struct.unpack(data)
    (magic, max_tables, max_rows_x_table, uuid_size) = unpacked
    if magic != self.magic:
      raise ValueError("Invalid index: magic value does not match")
    return magic, max_tables, max_rows_x_table, uuid_size

  def _LoadTables(self, file_obj=None, metadata=None):
    """Returns uuids of the tables in file_obj at the current offset.

    If no metadata is provided, it will try to fetch it from file_obj.
    In this case, it will assume the index starts at the start of the
    file_obj file start.
    """
    _metadata = metadata
    if _metadata is None:
      _metadata = self._LoadMetaData(file_obj=file_obj)
    table_nbytes = self.max_tables * self.table_struct.size
    table_data = file_obj.read(table_nbytes)

    tables = []
    offset = 0
    while offset < table_nbytes:
      (uuid_bytes,) = self.table_struct.unpack_from(table_data, offset)
      tables.append(utils.UUID(uuid_bytes))
      offset += self.table_struct.size
    return tables

  def _TableIndexToTableId(self, index=0):
    pass

  def AddTable(self, table=None):
    """Adds a table to the current index.

    You need to call Save() in order to index it.
    """
    self.tables.append(table.uuid)

  def GetRow(self, row_index=0):
    """Returns the corresponding (table_uuid, row_index) in the index."""
    if not self.file_obj:
      raise IndexNotLoadedError()
    self._SkipToRow(file_obj=self.file_obj, row_index=row_index)
    data = self.file_obj.read(self.row_struct.size)
    (table_index, row) = self.row_struct.unpack_from(data)
    return (self.tables[table_index], row)

  def _RowDataOffset(self):
    return (self.metadata_struct.size +
            self.table_struct.size * self.max_tables)

  def _SkipToRow(self, file_obj=None, row_index=0):
    """Skips to the index entry of row row_index."""
    offset = self._RowDataOffset() + self.row_struct.size * row_index
    file_obj.seek(offset, os.SEEK_SET)

  def ReadRow(self):
    raise NotImplemented

  def Save(self, file_obj=None, metatable=None):
    # TODO(parki): refactor save and store. decide on the interface to indexes
    logging.debug("Attempting to save metatable %s" % metatable)
    file_obj.seek(0)
    self._StoreMetaData(file_obj=file_obj)
    for table in metatable.tables:
      self.AddTable(table=table)
    total_tables = self._StoreTables(file_obj=file_obj)
    assert (total_tables == self.max_tables)
    row_count = self._StoreData(file_obj=file_obj, metatable=metatable)
    self.row_count = row_count
    file_obj.seek(0)

  def _StoreMetaData(self, file_obj=None):
    data = self.metadata_struct.pack(self.magic,
                                     self.max_tables,
                                     self.max_rows_per_table,
                                     self.uuid_size)
    file_obj.write(data)

  def _StoreTables(self, file_obj=None):
    """Flushes the current tables to the disk file."""
    # Write the tables
    structs_written = 0
    for table_id in self.tables:
      buffer = self.table_struct.pack(table_id.bytes)
      file_obj.write(buffer)
      structs_written += 1
    while structs_written < self.max_tables:
      file_obj.write(self.table_struct.pack('\x00' * self.uuid_size))
      structs_written += 1
    return structs_written

  def _StoreData(self, metatable=None, file_obj=None):
    """Indexes the data from the tables in metatable to disk."""
    logging.debug("StoreData starting at offset %ld", file_obj.tell())
    if not self.tables:
      self.tables.extend([table.uuid for table in metatable.tables])
    table_curr_row = [0] * len(metatable.tables)
    table_max_row = [table.row_count for table in metatable.tables]
    table_order_column_index = [table.ColumnIndex(table.OrderColumn())
                                for table in metatable.tables]
    assert (len(table_curr_row)
            == len(table_max_row)
            == len(table_order_column_index))

    # Start by populating our dates
    table_dates = []
    table_index = []
    for i, table in enumerate(metatable.tables):
      # Take into account blank tables
      if table.row_count > 0:
        cell = table.Cell(row_index=0, column_index=table_order_column_index[i])
        logging.debug("cell is %s" % cell)
        logging.debug("table_dates is %s" % table_dates)
        position = bisect.bisect_left(table_dates, cell)
        logging.debug("cell position is %d" % position)
        table_dates.insert(position, cell)
        table_index.insert(position, i)
      # Post:
    #  - table_dates contains an ordered list of dates
    #  - table_index contains the table index of the date at the same
    # position in table_dates

    metatable_index_row = 0
    # While we have dates...
    while table_dates:
      # Obtain the table with the lowest date
      table_i = table_index.pop(0)
      # And remove the date from the date list
      _ = table_dates.pop(0)
      table = metatable.tables[table_i]

      # Store the reference to this table and row
      table_row_index = table_curr_row[table_i]
      logging.debug("%d: (%d, %d)", metatable_index_row, table_i,
                    table_row_index)
      self._AddRow(file_obj=file_obj,
                  table_index=table_i,
                  row=table_row_index)
      # The earliest date has been stored.
      # Now update the current_row for the metatable
      table_curr_row[table_i] += 1
      table_i_curr_row = table_curr_row[table_i]
      # See if we're done with it
      if table_i_curr_row >= table_max_row[table_i]:
        # No need to retrieve a new row, so we continue with the
        # current data
        logging.debug("Done with table %s", self.tables[table_i].hex)
      else:
        # table_i has more rows. Obtain the date and merge it
        next_row_table_i = table_i_curr_row
        next_column_table_i = table_order_column_index[table_i]
        cell = table.Cell(row_index=next_row_table_i,
                          column_index=next_column_table_i)
        position = bisect.bisect_left(table_dates, cell)
        table_dates.insert(position, cell)
        table_index.insert(position, table_i)
      metatable_index_row += 1
    self._FlushCache(file_obj=file_obj)
    data_size = file_obj.tell()
    logging.debug("Data size: %ld (%ld MB)", data_size,
                  int(data_size / 1024 * 1024))
    return metatable_index_row

  def _FlushCache(self, file_obj=None):
    """Flush any remaining rows to the stored index."""
    file_obj.write(''.join(self._out_cache))
    del self._out_cache[:]

  def _AddRow(self, file_obj=None, table_index=None, row=0):
    """Appends a new row to file_obj referencing the row on the table.

    WARNING: The table_index is the index of the table within the stored
    tables of the index, not necessarily the same as the index of the table
    on the metatable that contains it!
    """

    # Because we store the table uuids in table order, we don't need to
    # dereference the table
    logging.debug("+ (%ld, %ld)", table_index, row)
    if (table_index is None or table_index < 0
        or table_index > self.max_tables):
      raise ValueError("Invalid table index %ld." % table_index)

    # TODO(parki): Maybe make sure the row is not > table.row_count ?
    if row is None or row < 0:
      raise ValueError("Invalid row %ld for table %s."
                       % (row, self.tables))
    data = self.row_struct.pack(table_index, row)
    self._out_cache.append(data)
    if len(self._out_cache) > 1024:
      file_obj.write(''.join(self._out_cache))
      del self._out_cache[:]
