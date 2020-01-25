import csv
import sqlite3
import json
from os.path import join

def get_scrapped_cases_to_2019():
    P = r'C:\Users\andy\supreme-court-scrap-Jan2019\out\8864\all-cases.csv'
    P = open(P, 'r', encoding='utf-8')
    P = csv.DictReader(P, delimiter='\t')
    cases = {}
    question_mark_judges = 0
    for line in P:
        case = line['caseId']
        not_closed = line['status'] != 'סגור'
        if not_closed:
            continue
        for i in range(1, 16):
            attr = f'justice{i}'
            if line[attr] == '?':
                question_mark_judges += 1
                print(case)
                break

        judges = line['Njudges']
        if not judges or int(judges) < 3:
            continue

        url = None
        if line['file_path'] and line['file_name']:
            url =f'https://supremedecisions.court.gov.il/Home/Download?path={line["file_path"]}&fileName={line["file_name"]}&type=2'
        line['url'] = url
        cases[case] = line
    print(f'Question mark judges {question_mark_judges}')
    return cases








def get_copies():
    P = r'C:\Users\andy\baguette\baguette\merger\merged-cases-result.json'
    f = open(P, 'r', encoding='utf-8')
    j = json.load(f)
    copies = set()
    for c in ('copy', 'copy2'):
        d = j[c]
        for k, v in d.items():
            p1 = f'{k[:-4]}{k[-2:]}'
            p2 = f'{v[:-4]}{v[-2:]}'

            copies.add(p1)
            copies.add(p2)
    return copies


def get_cases_in_nemala():
    conn = sqlite3.connect(r'C:\Users\andy\supreme-court-scrap-Jan2019\db-2019-05-01.sqlite3')

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    conn.row_factory = dict_factory
    cases = set()

    rs = conn.execute('select * from poorslaves_document')
    for r in rs:
        metadata = r['metadata']
        j = json.loads(metadata)
        case = j['case_id']
        case = case.split()[1]
        cases.add(case)

    conn.close()
    print(f'{len(cases)} cases')
    return cases

def get_metadata(case_id):
    ROOT = r'C:\Users\andy\supreme-court-scrap-Jan2019'
    p = case_id.split('/')
    case = p[0]
    year = f'20{p[1]}'
    p = join(ROOT, 'decisions-by-case', year, f'{case}.txt')
    try:
        with open(p, 'r') as f:
            for line in f:
                j = json.loads(line)
                if case_id not in j['CaseDesc']:
                    bad = j["CaseDesc"].split()[1]
                    fix = j["CaseDesc"].replace(bad, case_id)
                    j["CaseDesc"] = fix
                return j
    except FileNotFoundError as e:
        return None

copies = get_copies()
cases_scrap = get_scrapped_cases_to_2019()
cases_nemala = get_cases_in_nemala()

to_add = cases_scrap.keys() - cases_nemala
to_add = to_add - copies


print(f'To add {len(to_add)}')
SQLF =  'insert-merged-files.sql'
missing = set()
with open(SQLF, 'w') as sqlf:
    sqlf.write('INSERT INTO poorslaves_document ')
    sqlf.write('(url, views, answers, contentType, metadata) VALUES ')
    is_first = True
    for case_id in to_add:
        case = cases_scrap[case_id]
        metadata = get_metadata(case_id)
        if metadata is None:
            print(f'No metadata {case_id}')
            continue

        if 'url' not in case or not case['url']:
            print(f'no url {case_id}')
            continue


        m = {'name': metadata['CaseName'] or '', 'case_id': metadata['CaseDesc'], 'source': 'Jan19'}
        m = json.dumps(m)
        m = m.replace("'", "''")
        url = case["url"]
        record = f'(\'{url}\', 1000, 0, \'text/html\', \'{m}\')'

        if is_first:
            is_first = False
        else:
            sqlf.write(',\n')

        sqlf.write('\t')
        sqlf.write(record)

    sqlf.write(';\n')