import tempfile
import os
import unittest
import datetime

from guidediary import DiaryRewriter,Entry

class TestEntry(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.dut = DiaryRewriter()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_addFile_exact_dup_of_inexact_dup(self):
        about_now = datetime.datetime.now()
        with open(os.path.join(self.tmpdir.name, 'tst.gcal'), 'wb') as f:
            Entry.writeEntries(f, [
                Entry.Entry(about_now, 'original'),
                Entry.Entry(about_now, 'unoriginal'),
                Entry.Entry(about_now, 'unoriginal'),
            ], sub_x00x00=True)
        with open(os.path.join(self.tmpdir.name, 'tst.gcal'), 'rb') as f:
            self.dut.addFile(f)
        stats = self.dut.getStats()
        self.assertEqual(stats['exact_dups'], 1)
        self.assertEqual(stats['nonexact_dups'], 1)
        self.assertEqual(stats['entries_added'], 1)

if __name__ == '__main__':
    unittest.main()
