# -*- coding: utf-8 -*-

from datetime import date, timedelta
from webclient import Webclient
from storage import Storage


def get_date(anything):
    if isinstance(anything, date):
        return anything
    if type(anything)== type(0):
        date.fromtimestamp(anything)
    if type(anything)== type(""):
        parts = anything.split("-")
        year, month, day = tuple(map(int, parts))
        return date(year, month, day)


def date_to_string(d):
    return "-".join(map(lambda x: str(x).zfill(2), [d.year, d.month, d.day]))

def date_to_path(d):
    y = str(d.year)
    m = str(d.month).zfill(2)
    d = str(d.day).zfill(2)
    return "/".join([y, m, d])

class DocumentType:

    def __init__(self, extension, type_number):
        self.extension=extension
        self.type_number = type_number

class Decision:

    FIELDS=  ["CaseDesc", "CaseName", "Type", "VerdictsDtString", "FileName", "Path", "Pages", "CaseNum", "Year", "SeqNum"]

    def __init__(self, map):
        for f in self.FIELDS:
            value = map.get(f, "")
            setattr(self, f, value)

class Case:
    FIELDS = ["CaseDesc", "CaseDt", "CaseId", "CaseNum"]

    def __init__(self, map):
        for f in self.FIELDS:
            value = map.get(f, "")
            setattr(self, f, value)

    def get_case(self):
        return self.CaseNum.split(" ")[1].split("/")

    def get_year(self):
        year = int(self.get_case()[1])
        if year < 48:
            return "20%s" % year
        else:
            return "19%s" % year

    def get_case_number(self):
        return self.get_case()[0]

    def is_confidential(self):
        return self.CaseDesc and u"פרטי התיק חסויים" in self.CaseDesc

class Document:

    def __init__(self, decision, text, type):
        self.decision = decision
        self.text = text
        self.type = type

class SupremeCourt:

        TYPE_PDF=DocumentType("pdf", 4)
        TYPE_HTML=DocumentType("html", 2)
        TYPE_DOCX=DocumentType("doc", 5)
        TYPE_ALL=[TYPE_PDF, TYPE_HTML, TYPE_DOCX]

        def __init__(self, output_dir):
            self.webclient = Webclient()
            self.storage = Storage(output_dir)

        def scrap_time_span(self, first, last):
            current = last
            one_day = timedelta(1)
            while True:
                print "Scrapping %s" % current
                self.scrap_full_day(current)
                current = current - one_day
                if current < first:
                    break

        def get_decisions_by_day_case_opened(self, day):
            day = get_date(day)
            cases = self.get_cases_by_day_open(day)
            self.storage.save_records("cases-by-day-open", date_to_path(day), cases)
            print "got %s cases" % len(cases)
            for case in cases:
                year = case.get_year()
                number = case.get_case_number()




                decisions = self.get_decisions_by_case(year, number)
                print "%s decisions" % len(decisions)
                self.storage.save_records("decisions-by-case", "%s/%s" % (year, number), decisions)
                for i, d in enumerate(decisions):
                    document = self.download_document(d, SupremeCourt.TYPE_HTML)
                    if document is not None:
                        self.save_document(i, document)

                if case.is_confidential():
                    self.storage.save_records("confidential_cases", "%s/%s" % (year, number), [case])
                    print "Confidential"
                    continue

                self.get_case_metadata(case)


        def get_cases_by_day_open(self, day):
            d = get_date(day)
            d = d - timedelta(1)
            s = date_to_string(d)
            print "getting cases by day open %s" % s
            request = {"req": {"SearchText": None, "Year": None, "CaseNum": None, "dateType": 2, "publishDate": None,
                               "PublishFrom": "%sT21:00:00.000Z" % s, "PublishTo": "%sT22:00:00.000Z" % s,
                               "translationDateType": None, "translationPublishFrom": "2017-10-31T17:24:27.461Z",
                               "translationPublishTo": "2017-10-31T17:24:27.461Z"}, "lang": "1"}
            import urllib2
            try:
                r = self.webclient.query_server("GetCasesByDateOpen", request)
            except urllib2.HTTPError, e:
                pass
            return [Case(x) for x in r]

        def get_decisions_by_case(self, year, caseNum):
            query={"document":{"Year":year,"Counsel":[{"Text":"","textOperator":2,"option":"2","Inverted":False,
                 "Synonym":False,"NearDistance":3,"MatchOrder":False}],"CaseNum":"%s" % caseNum,"Technical":None,
                   "fromPages":None,"toPages":None,"dateType":1,"PublishFrom":None,"PublishTo":None,"publishDate":"8",
                   "translationDateType":1,"translationPublishFrom":"2017-09-30T17:06:14.777Z","translationPublishTo":
                   "2017-10-31T18:06:14.778Z","translationPublishDate":8,"SearchText":None,"Judges":None,"Parties":
                   [{"Text":"","textOperator":2,"option":"2","Inverted":False,"Synonym":False,"NearDistance":3,
                 "MatchOrder":False}],"Mador":None,"CodeMador":[],"TypeCourts":None,"TypeCourts1":None,
               "TerrestrialCourts":None,"LastInyan":None,"LastCourtsYear":None,"LastCourtsMonth":None,"LastCourtCaseNum"
                :None,"Old":False,"JudgesOperator":2,"Judgment":None,"Type":None,"CodeTypes":[],"CodeJudges":[],
               "Inyan":None,"CodeInyan":[],"AllSubjects":[{"Subject":None,"SubSubject":None,"SubSubSubject":None}],
               "CodeSub2":[],"Category1":None,"Category2":None,"Category3":None,"CodeCategory3":[],"Subjects":None,
                   "SubSubjects":None,"SubSubSubjects":None},"lan":1}

            print "get decisions by case %s/%s" % (year, caseNum)
            r = self.webclient.query_server("SearchVerdicts", query)
            return [Decision(row) for row in r]

        def get_case_metadata(self, case):
            if isinstance(case, Case):
                year = case.get_year()
                caseNum = case.get_case_number()
            elif isinstance(case, type("")):
                year = int(case.split("/")[1])
                if year < 48:
                    year = "20%s" % year
                else:
                    year = "19%s" % year
                caseNum = case.split("/")[0]
            url = "https://elyon2.court.gov.il/Scripts9/mgrqispi93.dll?Appname=eScourt&Prgname=GetFileDetails_for_new_site&Arguments=-N%s-%s-0" % (year, caseNum.zfill(6))
            print "case_metadata %s/%s" % (year, caseNum)
            the_page = self.webclient.download_url(url)
            self.storage.save_document("metadata", "%s/%s" % (year, caseNum), "html", the_page);




        def get_decisions_for_day(self, day):
            d = get_date(day)
            s = date_to_string(d)
            query={"document":{"Year":None,"Counsel":[{"Text":"","textOperator":2,"option":"2","Inverted":False,
                                                       "Synonym":False,"NearDistance":3,"MatchOrder":False}],
                               "CaseNum":None,"Technical":None,"fromPages":None,"toPages":None,"dateType":2,
                               "PublishFrom":"%sT21:00:00.000Z" % s,"PublishTo":"%sT21:00:00.000Z" % s,
                               "publishDate":None,"translationDateType":1,"translationPublishFrom":"2017-09-28T17:17:06.031Z",
                               "translationPublishTo":"2017-10-28T17:17:06.031Z","translationPublishDate":8,"SearchText":None,
                               "Judges":None,"Parties":[{"Text":"","textOperator":2,"option":"2","Inverted":False,"Synonym":False,
                                "NearDistance":3,"MatchOrder":False}],"Mador":None,"CodeMador":[],"TypeCourts":None,
                               "TypeCourts1":None,"TerrestrialCourts":None,"LastInyan":None,"LastCourtsYear":None,
                               "LastCourtsMonth":None,"LastCourtCaseNum":None,"Old":False,"JudgesOperator":2,"Judgment":None,
                               "Type":None,"CodeTypes":[],"CodeJudges":[],"Inyan":None,"CodeInyan":[],"AllSubjects":
                                   [{"Subject":None,"SubSubject":None,"SubSubSubject":None}],
                               "CodeSub2":[],"Category1":None,"Category2":None,"Category3":None,"CodeCategory3":[],"Subjects":None,"SubSubjects":None,"SubSubSubjects":None},"lan":1}

            data = self.webclient.query_server("SearchVerdicts", query)
            r = []
            for v in data:
                r.append(Decision(v))

            return r

        def download_document(self, decision, document_type):
            if decision.Path is None or decision.FileName is None:
                return None
            url = "https://supremedecisions.court.gov.il/Home/Download?path=%s&fileName=%s&type=%s" % (decision.Path, decision.FileName, document_type.type_number)
            text = self.webclient.download_url(url)
            if text is None:
                return None
            return Document(decision, text, document_type)

        def save_document(self, index, document):
            extension = document.type.extension

            verdict_date = document.decision.VerdictsDtString or "00/00/0000"
            index = str(index).zfill(4)

            parts = verdict_date.split("/")
            ymd = "%s-%s-%s-%s" % (index, parts[2], parts[1], parts[0])

            key = "%s/%s/%s" % (document.decision.Year, str(document.decision.CaseNum).zfill(5), ymd)
            if document.text:
                self.storage.save_document(extension, key, extension, document.text)
            else:
                self.storage.save_document("error-%s" % extension, key, extension, "")

        def close(self):
            pass