
import traceback

class MyCsv:

    def __init__(self, file, fields):
        self.file = file
        self.fields = fields

    def writeheader(self):
        self.file.write("\t".join(self.fields))
        self.file.write("\n")

    def writerow(self, m):
        items = [self._str(m.get(f, "")) for f in self.fields]
        try:
            last = len(items) - 1
            for i, item in enumerate(items):
                self.file.write(item)
                if i < last:
                    self.file.write('\t')
        except:
            print(traceback.format_exc())
            print()
            raise
        self.file.write("\n")

    def _str(self, x):
        if x == None:
            return ""
        return str(x)

    def close(self):
        self.file.close()