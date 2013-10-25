import unittest

from logally.lib import datatypes


class TestDataTypes(unittest.TestCase):
  def testDatetimeType(self):
    d1 = datatypes.DatetimeType("2012")
    # Test encoding/decoding
    self.assertEqual(d1.value, d1.Decode(d1.Encode(d1.value)))
    # Test different values
    self.assertRaises(ValueError, datatypes.DatetimeType, None)
    self.assertRaises(ValueError, datatypes.DatetimeType.Encode, None)

