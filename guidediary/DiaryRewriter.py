import logging
import datetime

from .Entry import Entry, writeEntries, parseEntries
from .Diary import Diary

def DiaryRewriterException(Exception):
    pass

class DiaryRewriter:
    def __init__(self):
        self.diary = Diary()
        self.exact_dups = []
        self.not_added = []
        self.logger = logging.getLogger(__name__)
        self.duplicates = []
        self.running_stats = { 'found_entries' : 0,
                               'exact_dups' : 0,
                               'nonexact_dups' : 0,
                               'entries_added' : 0,
        }

    def addFile(self, diary_f, swallow_duplicates=True):
        entries = parseEntries(diary_f, add_x00x00=True)
        for entry in entries:
            self.running_stats['found_entries'] += 1
            try:
                added = self.diary.addEntry(
                    entry, swallow_exact_duplicates=swallow_duplicates,
                    timeclash_resolution='older'
                )
                if not added:
                    self.exact_dups.append(entry)
                    self.running_stats['exact_dups'] += 1
                else:
                    self.running_stats['entries_added'] += 1
            except self.diary.__class__.DuplicateException as ex:
                if entry in self.not_added:
                    self.exact_dups.append(entry)
                    self.running_stats['exact_dups'] +=1
                else:
                    self.logger.warn('Duplicate: ' + repr(ex.diff))
                    self.not_added.append(entry)
                    self.duplicates.append(ex.diff)
                    self.running_stats['nonexact_dups'] += 1
        self.logger.info('Added %d entries from %s' % (len(entries), diary_f.name))

    def writeFile(self, diary_f):
        entries = self.diary.getSortedEntries()
        date = datetime.datetime.min
        for entry in entries:
            if entry.date <= date:
                raise DiaryRewriterException('Duplicate or unordered datetimes: ' + repr(entry))
        writeEntries(diary_f, entries, sub_x00x00=True)
        self.logger.info('Wrote %d entries to %s' % (len(entries), diary_f.name))

    def getExactDups(self):
        return sorted(self.exact_dups)

    def writeExactDupsFile(self, exact_dups_f):
        exact_dups = self.getNotAdded()
        for entry in exact_dups:
            exact_dups_f.write(entry.asText())
            exact_dups_f.write('\n\n')

    def getNotAdded(self):
        return sorted(self.not_added)

    def writeNotAddedFile(self, not_added_f):
        not_added = self.getNotAdded()
        for entry in not_added:
            not_added_f.write(entry.asText())
            not_added_f.write('\n\n')

    def getDiary(self):
        return self.diary

    def getNonexactDuplicates(self):
        return sorted(self.duplicates, key=lambda a: a.e1.date)

    def getStats(self):
        assert self.running_stats['exact_dups'] == len(self.getExactDups())
        assert self.running_stats['nonexact_dups'] == len(self.not_added)
        assert self.running_stats['nonexact_dups'] == len(self.getNonexactDuplicates())
        assert self.running_stats['entries_added'] == (
            self.running_stats['found_entries'] - self.running_stats['exact_dups']
            - self.running_stats['nonexact_dups'])
        return self.running_stats
