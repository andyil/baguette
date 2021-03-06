# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import Translations
import re

class DecisionParser:

    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')

    def get_words(self):
        strings = list(self.soup.stripped_strings)
        joined = "".join(strings)
        return len(joined.split(" "))

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
                continue
            if stripped_strings[0] in (Translations.BIFNEI, Translations.LIFNEI):
                stripped_strings = stripped_strings[1:]
                if not stripped_strings:
                    continue

            joined = "".join(stripped_strings)
            joined = joined.replace("\n", " ")
            if joined in (u"בפני:", u"לפני:"):
                continue
            if joined.startswith(Translations.BIFNEI) or joined.startswith(Translations.LIFNEI):
                pass
            if ":" in joined:
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
                            if str(s).strip() in Translations.judge_honor_title:
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
        import re
        s = s.replace("\n", " ")
        s = re.sub(" +", " ", s)
        j_full_title = None
        for title in Translations.judge_honor_title.keys():
            if s.startswith("%s " % title):
                j_full_title = title.replace(u"כבוד", "").strip()
                s = s.replace(title, "")
                s = s.strip()
                break
        else:
            pass

        if j_full_title is None:
            pass

        j_name = s
        gender = Translations.judge_honor_title[title]["gender"]
        j_title = Translations.judge_honor_title[title]["english"]

        retired = False
        if Translations.retired in j_name:
            j_name = j_name.replace(Translations.retired, "").strip()
            retired = True
        j_name = re.sub(" +", " ", j_name)
        return {"name": j_name, "title": j_title, "gender": gender, "full_title": j_full_title, "retired": retired}

if False:

    f = r"C:/Users/andy/supreme-court/documents/html/2010/01213/0015-2012-02-23.html"
    dp = DecisionParser(file(f, "r").read().decode('Windows-1255', 'strict'))
    judges = dp.get_judges()
    print (judges)
    exit(0)
    #C:\Users\andy\supreme-court\documents\metadata\2010\31.html