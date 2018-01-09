
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup

class DecisionParser:

    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')


    def get_judges(self):
        msoTables = self.soup.find_all("table", class_="MsoNormalTable")
        in_table = self.find_inside_table(msoTables)
        if in_table:
            return in_table
        for table in msoTables:
            if self.has_bifnei(table):
                judges = self.get_judges_from_table(table)
                return judges

        return self.judges_by_body_ruller()

    def judges_by_body_ruller(self):
        r = []
        brs = self.soup.find_all("p", class_="BodyRuller")
        for br in brs:
            sp = br.span
            stripped_strings = list(sp.stripped_strings)
            if not stripped_strings:
                break
            j = stripped_strings[-1]
            parsed = self.parse_judge_string(j)
            r.append(parsed)

        if not r:
            return None
        return r

    def find_inside_table(self, msoTables):
        for t in msoTables[:3]:
            all_cells = t.find_all("td")
            for cell in all_cells:
                s = "".join(cell.strings)
                if u"בפני:" in s or u"לפני:" in s:
                    parent = cell.parent
                    judge = "".join(parent.find_all("td")[1].strings)
                    judge = judge.strip()
                    return [self.parse_judge_string(judge)]


    def has_bifnei(self, table):
        first_cell = table.find("td")

        p = first_cell.p
        strings = p.strings

        s = "".join(strings)
        s = s.strip()
        if s == u"בפני:" or s ==u"לפני:":
            return True

    def get_judges_from_table(self, table):
        rows = table.find_all("tr")
        judges = []
        for row in rows:
            tds = row.find_all("td")
            last_td = tds[-1]
            judge = last_td.p.span
            str = judge.string
            if str == None:
                xs =[x for x in judge.strings]
                str = "".join(xs)
            judges.append(self.parse_judge_string(str))
            # $(".msoNormalTable")
        return judges

    def parse_judge_string(self, s):

        s = s.replace("\n", " ")
        parts = [_ for _ in s.split(" ") if _]


        j_full_title = parts[1]
        offset = 2
        if j_full_title == u"המשנה":
            j_full_title =" ".join(parts[1:3])
            offset = 3
        j_title = j_full_title
        j_name = " ".join(parts[offset:])
        gender = "m"
        if len(j_full_title) == 0:
            print ""
        elif j_full_title[-1] == u"ה" or j_full_title[-1] == u"ת":
            gender = "f"
            j_title = j_full_title[:-1]
        if j_full_title[0]== u"ה":
            j_full_title = j_full_title[1:]
        if j_title[0] == u"ה":
            j_title = j_title[1:]
        return {"name": j_name, "title": j_title, "gender": gender, "full_title": j_full_title}

if False:

    f = r"C:\Users\andy\supreme-court\documents\html\2010\00751\0001-2012-02-08.html"
    dp = DecisionParser(file(f, "r").read().decode('windows-1255', 'ignore'))
    judges = dp.get_judges()
    print judges
    exit(0)