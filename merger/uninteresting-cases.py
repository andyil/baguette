from os.path import dirname, join
from csv import DictReader
import json

PATH=r'C:\Users\andy\supreme-court-scrap\out\54456'
FILE = join(PATH, 'all-cases.csv')

interesting_types = {
    u"ע\"פ" : "Criminal Appeal",
    u"ע\"א" : "Civil Appeal",
    u"ע\"מ" : "Administrative Appeal",
    u"בג\"ץ" : "High Court of Justice",
    u"עע\"מ" : "Administrative Appeal",
    u"א\"ב" : "Election Approval",
    u"ע\"ב" : "Election Appeal",
    u"דנ\"א" : "Civil Further Hearing",
    u"דנ\"פ" : "Criminal Further Hearing",
    u"דנ\"מ" : "Administrative Further Hearing",
    u"דנג\"ץ" : "High Court of Justice Further Hearing",
    u"מ\"ח" : "Criminal Retrial"
}


uninteresting_cases = set()
ok_cases = set()
with open(FILE, 'r', encoding='utf-8') as f:
    r = DictReader(f, delimiter='\t')
    for line in r:
        caseId = line['caseId']

        legalProcedureHebrew = line['legalProcedureHebrew']
        confidential = line['Confidential']
        if confidential or legalProcedureHebrew not in interesting_types:
            uninteresting_cases.add(caseId)
        else:
            ok_cases.add(caseId)

OUT = join(dirname(__file__), 'uninteresting-cases.json')

open(OUT, 'w').write(json.dumps(list(uninteresting_cases)))

exit(0)
