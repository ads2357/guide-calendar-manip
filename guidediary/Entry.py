import logging
import struct
import sys
import datetime
import collections
import argparse
import json
import itertools

PADDING_BYTES = b' ' * 50
ENDMARK_BYTES = b'\x01\x00'
END_ZERO_BYTES = b'\x00' * 8

ENTRY_LENGTH_BYTES = 576
DATE_LENGTH_32bit = 4
PAD_LENGTH_8bit = len(PADDING_BYTES)
ENDMARK_LENGTH_8bit = len(ENDMARK_BYTES)
END_ZERO_LENGTH_8bit = len(END_ZERO_BYTES)
CONTENT_LENGTH_8bit = ENTRY_LENGTH_BYTES - (
    DATE_LENGTH_32bit * 4 +
    PAD_LENGTH_8bit * 1 +
    ENDMARK_LENGTH_8bit * 1 +
    END_ZERO_LENGTH_8bit * 1
)

FMT_STR = '<' + (''
                 + str(DATE_LENGTH_32bit) + 'I'
                 + str(PAD_LENGTH_8bit) + 's'
                 + str(CONTENT_LENGTH_8bit) + 's'
                 + str(ENDMARK_LENGTH_8bit) + 's'
                 + str(END_ZERO_LENGTH_8bit) + 's')

BINARY_FORMAT = struct.Struct(FMT_STR)
TEXT_CODEC = 'latin1'

RawEntry = collections.namedtuple(
    'RawEntry', 'year month day hour prepad content suffix zeroend')

class Entry:
    """Python representation of a diary entry"""
    def __init__(self, date, text, raw):
        self.date = date
        self.text = text
        self.raw  = raw

    def getRaw(self):
        return self.raw

    def getDate(self):
        return self.date

    def getText(self):
        return self.text

    def __lt__(self,other):
        if isinstance(other, self.__class__):
            return self.date < other.date
        return NotImplemented

    def __le__(self,other):
        if isinstance(other, self.__class__):
            return self.date <= other.date
        return NotImplemented

    def __eq__(self,other):
        if isinstance(other, self.__class__):
            return (self.date == other.date and
                    self.text.strip().lower() == other.text.strip().lower())
        return NotImplemented

    def __gt__(self,other):
        if isinstance(other, self.__class__):
            return self.date > other.date
        return NotImplemented

    def __ge__(self,other):
        if isinstance(other, self.__class__):
            return self.date >= other.date
        return NotImplemented

    def __str__(self):
        return str(self.date) + ':   ' + self.text.strip()[:10] + '...'

    def __repr__(self):
        return 'Entry(' + str(self.date) + ', "' + self.text.strip()[:10] + '...")'

    def asText(self):
        return self.dateAsText() + ' ' + self.text.strip()

    def dateAsText(self):
        return self.date.strftime('%Y %B %d %A')

    def toDict(self):
        return { 'date' : self.date.isoformat(),
                 'text' : self.text.strip(),
                 'raw'  : self.raw
        }

class Diff:
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2

    def __repr__(self):
        return (''
                + '-' + str(self.e1.date) + '\n'
                + '+' + str(self.e2.date) + '\n'
                + '-' + repr(self.e1.text) + '\n'
                + '+' + repr(self.e2.text))

    def __str__(self):
        return (''
                + self.e1.dateAsText() + '.\n'
                + 'Old entry: ' + self.e1.text.strip() + '.\n'
                + 'New entry: ' + self.e2.text.strip() + '.')

    def __eq__(self,other):
        if isinstance(other, self.__class__):
            return (self.e1 == other.e1 and
                    self.e2 == other.e2)
        return NotImplemented

class BinaryFormatException(Exception):
    pass

def writeEntries(diary_f, entries, **kwargs):
    """Write the file ('wb') from the list of Entries in order"""
    for (ii,entry) in zip(itertools.count(0),entries):
        rawEntry = RawEntry(
            entry.getDate().year, entry.getDate().month, entry.getDate().day, entry.getDate().hour,
            PADDING_BYTES, entry.getRaw(),
            ENDMARK_BYTES, END_ZERO_BYTES)
        entry_bytes = BINARY_FORMAT.pack(*rawEntry)
        assert len(entry_bytes) == ENTRY_LENGTH_BYTES
        isLastEntry = ii + 1 == len(entries)
        if kwargs.get('sub_x00x00', False) and isLastEntry:
            diary_f.write(entry_bytes[:-2])
        else:
            diary_f.write(entry_bytes)

def parseEntries(diary_f, **kwargs):
    """Read the file ('rb') and output a list of Entries in order"""
    logger = logging.getLogger(__name__)
    diary_bytes = diary_f.read()
    if kwargs.get('add_x00x00', False):
        diary_bytes += b'\x00'*2
    transform_bytes = kwargs.get('transform_bytes', lambda x: x)
    logger.info('Number of bytes: %d = %d (mod %d)' %
                 (len(diary_bytes), len(diary_bytes) % ENTRY_LENGTH_BYTES, ENTRY_LENGTH_BYTES))
    assert isinstance(diary_bytes, bytes)

    ret_EntryList = []

    for fields in BINARY_FORMAT.iter_unpack(diary_bytes):
        rawEntry = RawEntry._make(fields)
        if rawEntry.prepad != PADDING_BYTES:
            raise BinaryFormatException('Bad prepadding: ' + repr(rawEntry.prepad))
        elif rawEntry.suffix != ENDMARK_BYTES:
            raise BinaryFormatException('Wrong suffix: ' + repr(rawEntry.suffix))
        elif rawEntry.zeroend != END_ZERO_BYTES:
            raise BinaryFormatException('Wrong zeroend: ' + repr(rawEntry.zeroend))

        date = datetime.datetime(rawEntry.year, rawEntry.month, rawEntry.day, rawEntry.hour)
        text = rawEntry.content.decode(TEXT_CODEC)
        bytestring = transform_bytes(rawEntry.content)
        assert len(bytestring) == len(rawEntry.content)
        entry = Entry(date, text, bytestring)
        ret_EntryList.append(entry)

    return ret_EntryList

def main(args):
    logger = logging.getLogger(__name__)
    logger.basicConfig(level=logging.DEBUG)
    USAGE = args[0] + ' calendar_file'
    argObj = argparse.ArgumentParser(USAGE)

    argObj.add_argument('filename')

    args = argObj.parse_args(args[1:])

    try:
        with open(args.filename, 'rb') as f:
            entries = parseEntries(f)
    except struct.error as e:
        with open(args.filename, 'rb') as f:
            logger.warning('missing 2 bytes at the end')
            entries = parseEntries(f, add_x00x00 = True)
    print('found %d entries' % len(entries))

if __name__ == "__main__":
    main(sys.argv)
