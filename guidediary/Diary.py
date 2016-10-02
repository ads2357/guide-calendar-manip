import logging
import json

from .Entry import Entry, Diff

class Diary:
    class DiaryException(Exception):
        pass

    class DuplicateException(DiaryException):
        def addDiff(self,diff):
            self.diff = diff

    def __init__(self):
        self.entries = []
        self.logger = logging.getLogger(__name__)
        
    def addEntry(self, entry, **kwargs):
        self.logger.debug('Accepting entry: ' + str(entry))
        swallow_exact_duplicates = kwargs.get('swallow_exact_duplicates', False)
        timeclash_resolution = kwargs.get('timeclash_resolution', None)
        
        for e in self.entries:
            if e.date == entry.date:
                if not (swallow_exact_duplicates and entry == e):
                    ex = self.__class__.DuplicateException("Duplicate entry: " + str(e))
                    ex.addDiff(Diff(e,entry))
                    if timeclash_resolution:
                        if timeclash_resolution == 'older':
                            pass
                        else:
                            raise ValueException(
                                'Timeclash resolution should be in ["older"]')
                    else:
                        raise NotImplementedError("Cannot currently remove duplicates")
                    raise ex
                else:
                    self.logger.debug('Ignoring exact match.')
                    return False
        self.entries.append(entry)
        return True

    def getSortedEntries(self):
        return sorted(self.entries)

    def toJSON(self):
        return json.dumps([entry.toDict() for entry in self.entries],
                          indent=4)

def main():
    logging.basicConfig(level=logging.DEBUG)
    import datetime
    d = Diary()
    td = datetime.timedelta(1)
    e0 = Entry(datetime.datetime.now(), 'e0')
    e1 = Entry(datetime.datetime.now() + td, 'e1')
    e2 = Entry(datetime.datetime.now() + 2*td, 'e2')

    d.addEntry(e0)
    d.addEntry(e2)
    d.addEntry(e1)

    print(d.getSortedEntries())
    
if __name__ == "__main__":
    main()
