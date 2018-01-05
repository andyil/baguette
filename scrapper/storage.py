from os.path import expanduser, join, dirname, exists, sep
from json import dumps
from os import makedirs

class Storage:

    def __init__(self, output_dir):
       self.basedir = self._fix_path(output_dir)

    def _fix_path(self, path):
        path = path.replace("/", sep)
        path = path.replace("\\", sep)
        return path

    def save_records(self, category, key, records):
        path = join(self.basedir, self._fix_path(category), self._fix_path(key))
        filename = "%s.txt" % path

        directory = dirname(filename)
        if not exists(directory):
            makedirs(directory, 0777)

        f = open(filename, "wb")

        for r in records:
            f.write(dumps(r.__dict__))
            f.write("\n")
        f.close()

    def save_document(self, category, key, extension, document):
        path = join(self.basedir, "documents", category, key)
        filename = "%s.%s" % (path, extension)
        directory = dirname(filename)
        if not exists(directory):
            makedirs(directory, 0777)

        f = open(filename, "wb")
        f.write(document)
        f.close()
