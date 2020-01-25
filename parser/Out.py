# -*- coding: utf-8 -*-

from os import makedirs
from os.path import exists
import io

import Translations
import models
import MyCsv
from os.path import join
import DecisionParser



class Out:

    def __init__(self, directory):
        self.directory = directory
        if not exists(directory):
            makedirs(self.directory, 0o777)

        interestring = join(directory, "cases.csv")
        all_cases = join(directory, "all-cases.csv")
        judges = join(directory, "judges.csv")


        f_int = io.open(interestring, "w", encoding="utf-8")
        f_all = io.open(all_cases, "w", encoding="utf-8")
        f_judges = io.open(judges, "w", encoding="utf-8")
        k = models.CaseFields
        self.csv_all = MyCsv.MyCsv(f_all, k)
        self.csv_int = MyCsv.MyCsv(f_int, k)
        self.csv_judges = MyCsv.MyCsv(f_judges, models.JudgesFields)
        self.csv_all.writeheader()
        self.csv_int.writeheader()
        self.csv_judges.writeheader()


    def close(self):
        self.csv_all.close()
        self.csv_int.close()
        self.csv_judges.close()

    def dateOpenToDate(self, d):
        parts = d.split("/")
        return "%s-%s-%s" % (parts[2], parts[1], parts[0])

    def add_record(self, record):
        r = self.get_case_and_judges(record)
        if r is None:
            return
        case, judges = r
        dict = case.__dict__

        interesting = "uninterestingIssueId" not in dict

        extras = ["__module__", "__doc__", "uninterestingIssueId"]
        for e in extras:
            if e in dict:
                del dict[e]

        for k in dict.keys():
            if k not in models.CaseFields:
                print(f"Bad field {k}")
                exit(0)
        self.csv_all.writerow(dict)
        if interesting:
            self.csv_int.writerow(dict)

        for j in judges:
            j_dict = j.__dict__
            j_dict.update(dict)
            for e in extras:
                if e in j_dict:
                    del j_dict[e]
            self.csv_judges.writerow(j_dict)

    def get_case_and_judges(self, record):
        o = models.Case()
        if "confidential" in record and record["confidential"] == True:
            caseId = "%s-%s" % (record["case"], record["year"][:2])
            o.caseId = caseId
            o.Confidential = "1"

            return o, []
        gi = record["general_info"]
        case_num = gi["case_num"]

        parts = case_num.split(" ")

        o.caseId = parts[1]
        issueIdHebrew = parts[0]
        o.issueIdHebrew = issueIdHebrew
        issueId = Translations.translate_issue_type(parts[0])
        o.issueId = issueId

        if not Translations.is_interesting_type(issueIdHebrew):
            o.uninterestingIssueId = True

        caseName = u"%s נ' %s" % (gi["apellant"], gi["respondent"])
        o.caseName = caseName

        petitioners = self.get_side_attribute_by_role(record["sides"], "petitioner", "name")
        respondents = self.get_side_attribute_by_role(record["sides"], "respondent", "name")
        petitionersLawyers = self.get_side_attribute_by_role(record["sides"], "petitioner", "representative")
        respondentsLawyers = self.get_side_attribute_by_role(record["sides"], "respondent", "representative")

        for ii, p in enumerate(petitioners[0:3]):
            setattr(o, "petitioner%s" % (ii+1), p)
        for ii, p in enumerate(respondents[0:3]):
            setattr(o, "respondent%s" % (ii+1), p)

        for ii, p in enumerate([p for p in petitionersLawyers if p.strip][:3]):
            setattr(o, "lawyerP%s" % (ii+1), p)

        for ii, p in enumerate([p for p in respondentsLawyers if p.strip][:3]):
            setattr(o, "lawyerR%s" % (ii+1), p)

        o.NPetitioners = len(petitioners)
        o.NRespondents = len(respondents)


        if self.has_parliament_members(petitioners):
            o.parliament = "1"
        else:
            o.parliament = "0"

        low_case = None
        if record["lower_cases"]:
            low_case = record["lower_cases"][0]
            o.courtCaseSource = low_case["court"]
            o.numCaseSource = low_case["lower_court_case"]
            o.dateCaseSource = low_case["decision_date"]


        dateOpen = gi["submission_date"]
        o.dateOpen = self.dateOpenToDate(dateOpen)

        d = record["decisions"]
        last_decision = self.get_last_decision(d)
        judges_rows = []
        if last_decision:
            if "full_path" in last_decision:
                if exists(last_decision["full_path"]):
                    encodings = 'Windows-1255', 'utf-8'
                    for encoding in encodings:
                        try:
                            text = open(last_decision["full_path"], "r", encoding=encoding).read()
                            break
                        except UnicodeDecodeError as e:
                            if encoding == encodings[-1]:
                                return None
                            continue
                    dp = DecisionParser.DecisionParser(text)
                    judges= dp.get_judges()
                    words = dp.get_words()
                    o.Nwords = words
                    judges = judges or []
                    o.Njudges = len(judges)
                    for ji, j in enumerate(judges):
                        setattr(o, "justice%s" % (ji+1), j["name"])
                        judge_obj = models.Justice()
                        judge_obj.Name = j["name"]
                        judge_obj.Gender = j["gender"]
                        judge_obj.Retired = j["retired"]
                        judge_obj.Title = j["title"]
                        judges_rows.append(judge_obj)
            date_final_decision = self.dateOpenToDate(last_decision['VerdictsDtString'])
            o.dateFinalDecision = date_final_decision
            o.Npages = last_decision["Pages"]

        hearings = self.get_actual_hearings(record["sittings"])

        o.numHearings= len(hearings)
        if hearings:
            o.dateFArgument = hearings[0]["date"]
            o.dateLArgument = hearings[-1]["date"]

        o.LIssueArea = gi["section"]
        if low_case:
            parts = low_case["lower_court_case"].split(" ")
            lissue = "%s %s" % (gi["section"], parts[0])
            o.LIssue = lissue


        return o, judges_rows

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


if __name__=='__main__':
    directory = r'C:\Users\andy\elyon\documents\html\2010\07217'
    import os
    from os.path import join
    for f in os.listdir(directory):
        fp = join(directory, f)
        print(fp)

        encodings = 'Windows-1255', 'utf-8'
        for encoding in encodings:
            try:
                t = open(fp, 'r', encoding=encoding).read()
                print(encoding)
                break
            except UnicodeDecodeError as err:
                if encoding == encodings[-1]:
                    raise
                continue
