
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup

class MetadataParser:

    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')

    def all(self):
        self.json = {}
        if self.is_confidential():
            self.populate_confidential_case()
        else:
            self.parse_general_info()
            self.parse_lower_cases()
            self.parse_sides()
            self.parse_sittings()
            self.parse_events()
            self.parse_return_receipts()
            self.parse_petitions()
        return self.json


    def parse_petitions(self):
        self.json["petitions"] = self.parse_table("menu7")

    def parse_lower_cases(self):
        self.json["lower_cases"] = self.parse_table("menu3")

    def parse_sittings(self):
        self.json["sittings"] = self.parse_table("menu4")

    def parse_events(self):
        self.json["events"] = self.parse_table("menu5")

    def parse_sides(self):
        self.json["sides"] = self.parse_table("menu2")

    def parse_return_receipts(self):
        self.json["return_receipts"] = self.parse_table("menu6")

    def populate_confidential_case(self):
        self.json["petitions"] = []
        self.json["lower_cases"] = []
        self.json["sittings"] = []
        self.json["events"] = []
        self.json["sides"] = []
        self.json["return_receipts"] = []
        self.json["general_info"] = []

    def is_confidential(self):
        b = self.soup.find("b")
        confidential = b != None and b.string == u"אנו מצטערים"
        self.json["confidential"] = confidential
        return confidential

    def parse_general_info(self):
        div = self.soup.find("div", {"id": "menu1"})
        columns = div.find_all("div", {"class": "column"}, recursive=False)
        general_info = {}
        for column in columns:
            pairdivs = column.find_all("div", recursive = False)
            for pairdiv in pairdivs:
                label = pairdiv.find("span", {"class":"caseDetails-label"}).string.strip()
                info_string = pairdiv.find("span", {"class":"caseDetails-info"}).string
                if info_string == None:
                    info = ""
                else:
                    info = info_string.strip()
                general_info[self.tr(label)] = info
        self.json["general_info"] = general_info

    def is_table_empty(self, table):
        h4s = table.find_all("h4")
        for h4 in h4s:
            if h4.string != None and h4.string == u"לא נמצאו רשומות בתחום המבוקש.":
                return True
        return False

    def parse_table(self, divId):
        div = self.soup.find("div", {"id": divId})
        if self.is_table_empty(div):
            return []
        rows = div.table.tbody.find_all("tr", recursive=False)
        parsed_rows = []
        for row in rows:
            parsed_row = {}
            for cell in row.find_all("td", recursive=False):
                try:
                    dataLabel = cell["data-label"]
                    eng = self.tr(dataLabel)
                except KeyError:
                    eng = str(cell["class"][0])
                if cell.string:
                    parsed_row[eng] = cell.string.strip()
                elif cell.a and cell.a.string:
                    parsed_row[eng] = cell.a.string.strip()
                elif cell.a and cell.a["data-content"]:
                    judges = self.parse_sitting_judges(cell)
                    parsed_row[eng] = cell.contents[0].string.strip()
                    parsed_row["judges"] = judges
                if "date" in eng:
                    parsed_row[eng] = self.fix_date(parsed_row[eng])
            parsed_rows.append(parsed_row)
        return parsed_rows



    def parse_sitting_judges(self, cell):
        dataContent = cell.a["data-content"]
        parts = dataContent.split("<br>")
        judges = [p.strip() for p in parts if p.strip()]
        return judges

    def fix_date(self, date_string):
        parts = date_string.split()
        date = ""
        time = ""
        for p in parts:
            if "/" in p:
                date_parts = p.split("/")
                y = date_parts[2]
                m = date_parts[1]
                d = date_parts[0]
                date = "%s-%s-%s" % (y.zfill(4), m.zfill(2), d.zfill(2))
            if ":" in p:
                time = p

        if date and time:
            return "%s %s" %(date, time)
        else:
            return date


    def tr(self, heb):
        translation = {
            u"תאריך": "date",
            u"שעת דיון": "time",
            u"אולם": "hall",
            u"גורם שיפוטי": "judge",
            u"סטטוס": "status",

            u"סוג צד": "role",
            u"שם": "name",
            u"באי כוח": "representative",
            u"#": "seq",

            u"שם ב.משפט": "court",
            u"מ.תיק דלמטה": "lower_court_case",
            u"ת.החלטה": "decision_date",
            u"הרכב/שופט": "judge_tribunal",

            u"ארוע ראשי": "main_event",
            u"ארוע משני": "secondary_event",


            u"נמען": "receiver",
            u"תאריך חתימה": u"date_signed",

            u"תיאור בקשה": "petition_description",
            u"מגיש": "submitter",
            u"נדחה מהמרשם": "record_removed",

            u"מספר הליך": "case_num",
            u"מדור": "section",
            u"תאריך הגשה": "submission_date",
            u"סטטוס תיק": "status",
            u"מערער": "apellant",
            u"משיב": "respondent",
            u"אירוע אחרון": "last_event"
        }
        if heb not in translation:
            print "Missing!", heb
            exit(0)
        return translation[heb]


