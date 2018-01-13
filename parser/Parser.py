# -*- coding: utf-8 -*-

from os.path import join
from os import walk
import MetadataParser
import json
import Out


def load_decisions(directory, case_num, year):

    file = join(directory, "decisions-by-case", str(year), "%s.txt" %str(case_num))
    decisions = []
    for i, line in enumerate(open(file, "r")):
        decision = json.loads(line)
        decision["index"] = i
        date = decision["VerdictsDtString"]
        if date != None:
            parts = date.split("/")
            d = "-".join(parts[::-1])
            file = "%s-%s.html" % (str(i).zfill(4), d)
            full_path = join(directory, "documents", "html", year, case_num.zfill(5), file)
            decision["full_path"] = full_path
        decisions.append(decision)
    return decisions

class Parser:

    def __init__(self, directory):
        self.directory = directory
        self.out = Out.Out("%s-out" % directory)


    def parse(self):
        base = join(self.directory, "documents", "metadata")
        total = 0
        for dirName, subdirList, fileList in walk(base):
            print('Found directory: %s' % dirName)
            numbers = [int(x.replace(".html", "")) for x in fileList]
            numbers = sorted(numbers)
            for n in numbers:
                fname = "%s.html" % n
                print('\t%s' % fname)
                full_path = join(dirName, fname)
                total += 1
                self.parse_file(full_path)
                print "Parsed %s %s" % (total, full_path)

        self.out.close()


    def parse_file(self, full_path):
        f = open(full_path, "r")
        t = f.read()
        f.close()

        from os.path import dirname, basename

        year = basename(dirname(full_path))
        case = basename(full_path).replace(".html", "")
        return self.parse_text(case, year, t)


    def parse_text(self, case, year, text):
                m = MetadataParser.MetadataParser(text)
                parsed = m.all()
                decisions = load_decisions(self.directory, case, year)
                parsed["case"] = case
                parsed["year"] = year
                parsed["decisions"] = decisions
                self.out.add_record(parsed)

p = Parser(r"C:\Users\andy\supreme-court")
p.parse()