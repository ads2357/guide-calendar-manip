import tempfile
import os
import unittest

from guidediary import Entry

class TestEntry(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def createTstGcal(self, binary_content):
        with open(os.path.join(self.tmpdir.name, 'tst.gcal'), 'wb') as f:
            f.write(binary_content)

    def test_parseEntries_length(self):
        self.createTstGcal(bytes(420))
        with open(os.path.join(self.tmpdir.name, 'tst.gcal'), 'rb') as f:
            with self.assertRaises(Exception):
                Entry.parseEntries(f)

if __name__ == '__main__':
    unittest.main()
