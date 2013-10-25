import unittest

from logally.plugins.datasources import localfile


class LocalFileTest(unittest.TestCase):
  def testOpen(self):
    lfile = localfile.LocalFile(name="My local file")
    self.assertRaises(ValueError, lfile.Open)
    lfile.SetParameter(name="path",
                       value="tests/plugins/datasources/localfile_test.py")
    self.assertRaises(IOError, lfile.Read)
    lfile.Open()
    data = lfile.Read()


if __name__ == '__main__':
  unittest.main()
