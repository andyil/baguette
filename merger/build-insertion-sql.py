from os.path import join, dirname, exists
import json


def get_metadata(case):
    ROOT = r'C:\Users\andy\supreme-court-scrap'
    p = case.split('/')
    case = p[0]
    year = p[1]
    p = join(ROOT, 'decisions-by-case', year, f'{case}.txt')
    try:
        with open(p, 'r') as f:
            for line in f:
                j = json.loads(line)
                return j
    except FileNotFoundError as e:
        return None

P = join(dirname(__file__), 'merged-cases-result.json')
with open(P, 'r') as f:
    j = json.load(f)

to_add = j['to_add']

SQLF = join(dirname(__file__), 'insert-merged-files.sql')
missing = set()
with open(SQLF, 'w') as f:
    f.write('INSERT INTO poorslaves_document ')
    f.write('(url, views, answers, contentType, metadata) VALUES ')

    is_first = True
    for t in to_add:
        p = t.split(':',1)
        number = p[0]
        url = p[1]

        metadata = get_metadata(number)
        if not metadata:
            missing.add(number)
            continue
        m = {'name': metadata['CaseName'] or '', 'case_id': metadata['CaseDesc'], 'source': 'merged'}
        m = json.dumps(m)
        m = m.replace("'", "''")
        record = f'(\'{url}\', 1000, 0, \'text/html\', \'{m}\')'

        if is_first:
            is_first = False
        else:
            f.write(',\n')

        f.write('\t')
        f.write(record)

    f.write(';\n')

print(missing)
print(len(missing))

