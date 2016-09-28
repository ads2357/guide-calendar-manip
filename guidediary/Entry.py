import logging
import struct
import sys
import datetime
import collections
import argparse

ENTRY_LENGTH_BYTES = 576
DATE_LENGTH_32bit = 4
PAD_LENGTH_8bit = 25
ENDMARK_LENGTH_8bit = 2
END_ZERO_LENGTH_8bit = 8
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


class Entry:
    """Python representation of a diary entry"""
    def __init__(self, date, text):
        self.date = date
        self.text = text

    def getDate(self):
        return self.date

    def getText(self):
        return self.text

class BinaryFormatException(Exception):
    pass

def parseEntries(diary_f, **kwargs):
    """Read the file ('rb') and output a list of Entries in order"""
    diary_bytes = diary_f.read()
    if kwargs.get('add_x00x00', False):
        diary_bytes += b'\x00'*2
    logging.info('Number of bytes: %d = %d (mod %d)' %
                 (len(diary_bytes), len(diary_bytes) % ENTRY_LENGTH_BYTES, ENTRY_LENGTH_BYTES))
    assert isinstance(diary_bytes, bytes)

    RawEntry = collections.namedtuple(
        'RawEntry', 'year month day hour prepad content suffix zeroend')
    binary_format = struct.Struct(FMT_STR)

    ret_EntryList = []
    
    for fields in binary_format.iter_unpack(diary_bytes):
        rawEntry = RawEntry._make(fields)
        if rawEntry.prepad != b' ' * PAD_LENGTH_8bit:
            raise BinaryFormatException('Bad prepadding: ' + repr(rawEntry.prepad))
        elif rawEntry.suffix != b'\x01\x00':
            raise BinaryFormatException('Wrong suffix: ' + repr(rawEntry.suffix))
        elif rawEntry.zeroend != b'\x00'*8:
            raise BinaryFormatException('Wrong zeroend: ' + repr(rawEntry.zeroend))

        date = datetime.datetime(rawEntry.year, rawEntry.month, rawEntry.day, rawEntry.hour)
        content = rawEntry.content.decode('unicode_escape')
        
        entry = Entry(date, content)
        ret_EntryList.append(entry)

    return ret_EntryList

def main(args):
    logging.basicConfig(level=logging.DEBUG)
    USAGE = args[0] + ' calendar_file'
    argObj = argparse.ArgumentParser(USAGE)

    argObj.add_argument('filename')

    args = argObj.parse_args(args[1:])

    try:
        with open(args.filename, 'rb') as f:
            entries = parseEntries(f)
    except struct.error as e:
        with open(args.filename, 'rb') as f:
            logging.warn('missing 2 bytes at the end')
            entries = parseEntries(f, add_x00x00 = True)
    print('found %d entries' % len(entries))

if __name__ == "__main__":
    main(sys.argv)
