from os.path import join, dirname
import json
from baguette.merger import side_types

legalProcedureTranslations = None
legalProcedureAreaOfLaw = None

def translate_issue_area(s):
    m = {}
    m['פלילי תפח'] = 'Severe Crime Case'
    m['פלילי פח'] = 'Severe Crime Case'
    m['פלילי תפ'] = 'Criminal - Regular'
    m['פלילי תהג'] = 'Criminal - Extradition'
    m['פלילי פשר'] = 'Criminal - Bankruptcy'
    m['פלילי פ'] = 'Criminal - Regular'
    m['בגץ תא'] = 'High court of Justice'
    m['בגץ תא'] = 'High court of Justice'
    m['בגץ תא'] = 'High court of Justice'
    m['בגץ תא'] = 'High court of Justice'
    m['בגץ עע'] = 'High court of Justice'
    m['אזרחי תצ'] = 'Class Action'
    m['אזרחי תנג'] = 'Derivative action'
    m['אזרחי תמ'] = 'Tenders'
    m['אזרחי תאק'] = 'Civil Short Track'
    m['אזרחי תא'] = 'Civil Regular'
    m['אזרחי פשר'] = 'Bankruptcy'
    m['אזרחי פרק'] = 'Firm liquidation'
    m['אזרחי פ'] = 'Bankruptcy'
    m['אזרחי עתמ'] = 'Administrative Petition'
    m['אזרחי עשא'] = 'Other Civil Appeals'
    m['אזרחי עמא'] = 'Income tax'
    m['אזרחי עמ'] = 'Tax'
    m['אזרחי וע'] = 'Tax Tribunal Appeal'
    m['אזרחי הפ'] = 'Originating Motion'
    m['אזרחי הע'] = 'Antitrust'
    m['אזרחי הכ'] = 'Antitrust'
    m['אזרחי א'] = 'Civil Case - Regular'
    m['פלילי תהד'] = 'Criminal - Extradition'
    m['פלילי תד'] = 'Criminal - Traffic'
    m['פלילי ת'] = 'Criminal - Traffic'
    m['פלילי עפ'] = 'Criminal - Regular'
    m['אזרחי צ'] = 'Class Action'
    m['אזרחי פש'] = 'Bankruptcy'
    m['אזרחי עתם'] = 'Administrative Petition'
    m['אזרחי עתn'] = 'Administrative Petition'
    m['אזרחי עתא'] = 'Administrative Petition'
    m['אזרחי עת\''] = 'Administrative Petition'
    m['אזרחי מ'] = 'Administrative Petition'
    m['אזרחי עש'] = 'Tax'
    m['אזרחי עמה'] = 'Tax'
    m['אזרחי בשא'] = 'Civil - Intermediate request'
    m['אזרחי בש'] = 'Civil - Intermediate request'
    m['פלילי א'] = 'Criminal - Regular'


    return m.get(s, '')

def load_map(filename):
    p = join(dirname(__file__), filename)
    lines = open(p, 'rb').read().decode('utf-8').split('\n')
    lines = [l.strip() for l in lines]
    map = {}
    for ii in range(0, len(lines), 2):
        map[lines[ii]] = lines[ii + 1]
    return map


def legalProcedureTranslate(l):
    global legalProcedureTranslations
    if legalProcedureTranslations is None:
        legalProcedureTranslations = load_map('legalProcedure-translations.txt')
    return legalProcedureTranslations.get(l, '')

def legalProcedureTranslateAreaOfLaw(l):
    global legalProcedureAreaOfLaw
    if legalProcedureAreaOfLaw is None:
        legalProcedureAreaOfLaw = load_map('legalProcedure-translations-area.txt')
    return legalProcedureAreaOfLaw.get(l, '')

def fix_courtSourceInstance(value):
    value = value.replace('Labour', 'Labor')
    value = value.replace('Labour Court', 'Labor Court')
    value = value.replace('Labor Courts', 'Labor Court')
    value = value.replace('Military Courts', 'Military Court')
    value = value.replace('Military court', 'Military Court')
    return 'courtSourceInstance', value

def fix_numCaseSource(value):
    if value.startswith('חא'):
        return [('numCaseSource', value), ("courtSourceInstance", "Standard Contracts Court")]
    elif value.startswith('עחק'):
        return [('numCaseSource', value), ("courtSourceInstance", "Court of Admiralty")]
    else:
        return 'numCaseSource', value

def fix_courtSourceDistrict(value):
    if value == "Military Tribunal":
        return 'courtSourceDistrict', ""
    else:
        return 'courtSourceDistrict', value


def fix_casename(value):
    fixed = " ".join(value.split()[2:])
    while fixed and fixed[0]=='"':
        fixed = fixed[1:]
    while fixed and fixed[-1]=='"':
        fixed = fixed[:-1]
    fixed = fixed.replace('""', '"')

    legalProcedureHebrew = value.split()[0]
    legalProcedure = legalProcedureTranslate(legalProcedureHebrew)
    area = legalProcedureTranslateAreaOfLaw(legalProcedureHebrew)
    fixed = f'{legalProcedureHebrew} {value.split()[1]} {fixed}'
    return [('caseCitation', fixed),
            ('legalProcedureHebrew', legalProcedureHebrew),
            ('legalProcedure', legalProcedure),
            ('LIssue', area)]

def fix_caseCitation(value):
    return 'casename', value

def fix_Nwords(value):
    return 'Nwords', value.replace('s', '00')

def fix_Njudges(value):
    if value.strip() ==  '1':
        return 'Njudges', '3'
    return 'Njudges', value


def fix_LIssue(value):
    translated_issue_area = translate_issue_area(value)
    translated_issue_area_lower = translated_issue_area.lower()
    if 'civil' in translated_issue_area_lower and 'regular' in translated_issue_area_lower:
        translated_issue_area = 'Civil Case - Regular'
    return [('LIssueAreaHebrew', value),
            ('LIssueArea', translated_issue_area)]


def fix_LIssueArea(value):
    return None


def fix_LIssueAreaHebrew(value):
    return None

judge_data = None


def get_judge_data(name):
    global judge_data
    if judge_data is None:
        path = join(dirname(__file__), 'judge-metadata.json')
        f = open(path, 'r', encoding='utf-8')
        judge_data = json.load(f)
        f.close()

    return judge_data.get(name, {})

def fix_Name(n):
    data = get_judge_data(n)
    return [
        ('Name', n),
        ('Seniority', data.get('since', '')),
        ('Experience', data.get('previous', '')),
        ('Religion', data.get('religion', ''))
    ]
