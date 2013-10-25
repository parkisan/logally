#! /usr/bin/python

from logally import model
from logally.lib import datatypes
from plaso import formatters
from plaso.lib import errors
from plaso.lib import eventdata
from plaso.lib import storage

import cStringIO


class PlasoTable(model.Table):
  headers = [
    ('timestamp', datatypes.DatetimeType),
    ('long_description', datatypes.UTF8StringType),
  ]

  def Open(self):
    fd = open("plaso_test", "r")
    if not self.datasource:
      raise ValueError("No datasource selected")

    if self.is_open:
      return

    self.datasource.Open()
    self.plaso_table = storage.PlasoStorage(fd,
                                            read_only=True)
    self.plaso_prototables_meta =[]
    self._total_rows = 0
    for i in self.plaso_table.GetProtoNumbers():
      prototable_meta = self.plaso_table.ReadMeta(i)
      self.plaso_prototables_meta.append(prototable_meta)
      self._total_rows += prototable_meta['count']
    for col_data in self.headers:
      name, datatype = col_data
      column = model.Column(name=name, datatype=datatype)
      self.AppendColumn(column=column)
    self.is_open = True
    #self._events = []
    #for i in range(self._total_rows):
    #  self._events.append(self.plaso_table.GetSortedEntry())

  @property
  def row_count(self):
    return self._total_rows

  @row_count.setter
  def row_count(self, value):
    self._row_count = value

  def Cell(self, row_index=0, column_index=0):
    if row_index > self.row_count or row_index < 0:
      raise ValueError
    #prototable_i, relative_row = self._ProtoAndRowForAbsoluteRow(row_index)
    #print "%d: (%d, %d)" % (row_index, prototable_i, relative_row)
    event_object = self.plaso_table.GetEntry(1, row_index)
    #event_object = self._events[row_index]

    event_formatter = eventdata.EventFormatterManager.GetFormatter(event_object)
    if not event_formatter:
      raise errors.NoFormatterFound(
          u'Unable to find event formatter for: %s.' % event_object.DATA_TYPE)
    msg, msg_short = event_formatter.GetMessages(event_object)

    if column_index == 0:
      cell_data = datatypes.DatetimeType(event_object.timestamp / 1000000)
    elif column_index == 1:
      cell_data = msg
    else:
      raise ValueError("Unknown column index %d")
    return model.Cell(value=cell_data, column=self.ColumnAt(column_index))

  def _ProtoAndRowForAbsoluteRow(self, absolute_row):
    if absolute_row < 0 or absolute_row > self.row_count:
      raise ValueError

    prototable = 1
    accumulated_rows = 0
    for prototable_meta in self.plaso_prototables_meta:
      if absolute_row < (accumulated_rows + prototable_meta['count']):
        return prototable, (absolute_row - accumulated_rows)
      prototable += 1
      accumulated_rows += prototable_meta['count']
