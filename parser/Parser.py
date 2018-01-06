# -*- coding: utf-8 -*-

from os.path import join
from os import walk
import MetadataParser
import Translations
import json


def load_decisions(directory, case):
    parts = case.split("/")
    case_name = parts[0]
    case_num = case_name.split(" ")[1]
    year = parts[1]
    numeric_year = int(str(year))
    if numeric_year < 48:
        year = numeric_year+2000
    else:
        year = numeric_year+1900
    file = join(directory, "decisions-by-case", str(year), "%s.txt" %str(case_num))
    decisions = []
    for line in open(file, "r"):
        decision = json.loads(line)
        decisions.append(decision)
    return decisions

class Parser:

    def __init__(self, directory):
        self.directory = directory

    def parse(self):
        base = join(self.directory, "documents", "metadata")
        import Tables
        t = Tables.Tables()
        total = 0
        for dirName, subdirList, fileList in walk(base):
            print('Found directory: %s' % dirName)
            numbers = [int(x.replace(".html", "")) for x in fileList]
            numbers = sorted(numbers)
            for n in numbers:
                fname = "%s.html" % n
                print('\t%s' % fname)
                full_path = join(dirName, fname)
                parsed = self.parse_file(full_path)
                year = dirName.split("\\")[-1]
                casename = fname.replace(".html", "")
                t.add([("TITLE", "%s/%s" % (casename, year))]+parsed)
                total += 1
                if total == 1000:
                    break
        t.render()
        exit()


    def parse_file(self, full_path):
        f = open(full_path, "r")
        t = f.read()
        f.close()
        return self.parse_text(t)

    def get_side_attribute_by_role(self, sides, rolename, attribute):
        r = []
        for side in sides:
            role = side["role"]
            if Translations.translate_role(role) == rolename:
                r.append(side[attribute])
        return r

    def get_actual_hearings(self, hearings):
        r = []
        for h in hearings:
            if h["status"] == u"התקיים":
                r.append(h)
        return r

    def has_parliament_members(self, petitioners):
        for p in petitioners:
            if Translations.is_knesset_member(p):
                return True
        return False

    def get_last_decision(self, decisions):
        for d in decisions[::-1]:
            if Translations.translate_decision(d["Type"]) == "verdict":
                return d
        return None

    def parse_text(self, text):
        m = MetadataParser.MetadataParser(text)
        parsed = m.all()
        if "confidential" in parsed and parsed["confidential"] == True:
            print "Confidential"
            return [("Confidential", True)]
        gi = parsed["general_info"]
        case_num = gi["case_num"]

        parts = case_num.split(" ")

        o = []
        o.append(("caseId", parts[1]))
        issueIdHebrew =  parts[0]
        o.append(("issueIdHebrew",issueIdHebrew))
        issueId =Translations.translate_issue_type(parts[0])
        o.append(("issueId", issueId))

        if not Translations.is_interesting_type(issueIdHebrew):
            o.append(("uninterestingIssueId", "True"))
            return o

        caseName = u"%s נ' %s" % (gi["apellant"], gi["respondent"])
        o.append(("caseName", caseName))

        petitioners = self.get_side_attribute_by_role(parsed["sides"], "petitioner", "name")
        respondents = self.get_side_attribute_by_role(parsed["sides"], "respondent", "name")
        petitionersLawyers = self.get_side_attribute_by_role(parsed["sides"], "petitioner", "representative")
        respondentsLawyers = self.get_side_attribute_by_role(parsed["sides"], "respondent", "representative")

        for ii, p in enumerate(petitioners):
            o.append(("petitioner%s" % ii, p))
        for ii, p in enumerate(respondents):
            o.append(("respondent%s" % ii, p))
        for ii, p in enumerate(petitionersLawyers):
            if not p.strip():
                continue
            o.append(("lawyerP%s" % ii, p))
        for ii, p in enumerate(respondentsLawyers):
            if not p.strip():
                continue
            o.append(("lawyerR%s" % ii, p))

        o.append(("NPetitioners", len(petitioners)))
        o.append(("NRespondents", len(respondents)))

        if self.has_parliament_members(petitioners):
            o.append(("parliament", "1"))
        else:
            o.append(("parliament", "0"))

        low_case = None
        if  parsed["lower_cases"]:
            low_case = parsed["lower_cases"][0]
            o.append(("courtCaseSource", low_case["court"]))
            o.append(("courtCaseSource", low_case["lower_court_case"]))
            o.append(("dateCaseSource", low_case["decision_date"]))

        dateOpen = gi["submission_date"]
        o.append(("dateOpen", dateOpen))

        d = load_decisions(self.directory, case_num)
        lastDecision = self.get_last_decision(d)
        lastDecisionPages = ""
        if lastDecision:
            dateFinalDecisions = lastDecision['VerdictsDtString']
            o.append(("dateFinalDecisions",dateFinalDecisions))
            lastDecisionPages = lastDecision["Pages"]

        hearings = self.get_actual_hearings(parsed["sittings"])

        o.append(("numHearings", len(hearings)))
        if hearings:
            o.append(("dateFArgument", hearings[0]["date"]))
            o.append(("dateLArgument", hearings[-1]["date"]))


        o.append(("LIssueArea", gi["section"]))
        if low_case:
            parts = low_case["lower_court_case"].split(" ")
            lissue = "%s %s" % (gi["section"], parts[0])
            o.append(("LIssue", lissue))

        o.append( ("Npages", lastDecisionPages))

        return o

p = Parser(r"C:\Users\andy\supreme-court")
p.parse()