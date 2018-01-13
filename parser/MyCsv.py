


class MyCsv:

    def __init__(self, file, fields):
        self.file = file
        self.fields = fields

    def writeheader(self):
        self.file.write("\t".join(self.fields))
        self.file.write("\n")

    def writerow(self, m):
        items = [self._str(m.get(f, "")) for f in self.fields]
        self.file.write("\t".join(items).encode("utf8"))
        self.file.write("\n")

    def _str(self, x):
        if x == None:
            return ""
        return unicode(x)

    def close(self):
        self.file.close()