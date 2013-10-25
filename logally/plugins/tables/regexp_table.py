from PyQt4.QtCore import *
from PyQt4.QtGui import *
from logally import model


KNOWN_REGEXPS = {
  "syslog":
    {
      "regexp": r'(?P<m>[0-9A-z]+)\s+' \
                '(?P<d>[0-9]+)\s+' \
                '(?P<H>[0-9]+)[^0-9](?P<M>[0-9]+)[^0-9](?P<S>[0-9]+)\s+' \
                '(?P<host>[^ ]+)\s+' \
                '(?P<source>[^:]+):\s+' \
                '(?P<msg>.*)$',
      "columns": {
        "timestamp": "{m} {d} {H}:{M}:{S}",
        "host": "{host}",
        "source": "{source}",
        "msg": "{msg}"
      }
    },
}


class RegexpTable(model.Table):
  def __init__(self, regexp=None, skip_rows=0):
    pass
