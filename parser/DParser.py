# -*- coding: utf-8 -*-

from os.path import join
from os import walk
import MetadataParser
import Translations
import json

import DecisionParser

class DParser:

    def __init__(self, directory):
        self.directory = directory

    def parse(self):
        base = join(self.directory, "documents", "html")
        for dirName, subdirList, fileList in walk(base):
            print('Found directory: %s' % dirName)
            for fname in fileList:
                full_path =  join(dirName, fname)
                print full_path

                html = open(full_path, "r").read().decode('windows-1255', 'ignore')
                if "html" in html[0:100]:
                    dp = DecisionParser.DecisionParser(html)
                    judges = dp.get_judges()
                    if judges == None:
                        print ""
                    for j in judges:
                        print "\t%s" % j["name"]





p = DParser(r"C:\Users\andy\supreme-court")
p.parse()