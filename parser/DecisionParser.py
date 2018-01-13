
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import Translations

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

    def has_judge_honor_title(self, s):
        for t in Translations.judge_honor_title:
            if t in s:
                return True
        return False

    def find_inside_table(self, msoTables):
        for t in msoTables[:3]:
            all_cells = t.find_all("td")
            for cell in all_cells:
                s = "".join(cell.strings)
                if u"בפני:" in s or u"לפני:" in s:
                    parent = cell.parent.parent
                    tds = parent.find_all("td")
                    judges = []

                    for td in tds:
                        strings = list(td.strings)
                        strings = [s for s in strings if s.strip()]
                        if not u"כבוד" in "".join(strings):
                            continue
                        for ind, s in enumerate(strings):
                            if s in Translations.judge_honor_title:
                                j = "%s %s" % (s, strings[ind+1])
                                judges.append(self.parse_judge_string(j))
                            elif self.has_judge_honor_title(s):
                                judges.append(self.parse_judge_string(s))
                            else:
                                continue
                    return judges


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

        for title in Translations.judge_honor_title.keys():
            if s.startswith("%s " % title):
                j_full_title = title.replace(u"כבוד", "").strip()
                s = s.replace(title, "")
                s = s.strip()
                break

        j_name = s
        gender = Translations.judge_honor_title[title]["gender"]
        j_title = Translations.judge_honor_title[title]["english"]

        retired = False
        if Translations.retired in j_name:
            j_name = j_name.replace(Translations.retired, "").strip()
            retired = True
        return {"name": j_name, "title": j_title, "gender": gender, "full_title": j_full_title, "retired": retired}

if False:

    f = r"C:\Users\andy\supreme-court\documents\html\2010\00232\0008-2012-09-19.html"
    dp = DecisionParser(file(f, "r").read().decode('windows-1255', 'ignore'))
    judges = dp.get_judges()
    print judges
    exit(0)
    #C:\Users\andy\supreme-court\documents\metadata\2010\31.html