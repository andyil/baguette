import csv
from os.path import dirname, join
import re
import json

def fix_case(c):
    o = c
    c = c.replace('\\', '/')
    c = c.replace(',', '')
    c = c.strip()
    parts = c.split('/')

    if len(parts[1]) == 2:
        return f'{parts[0]}/20{parts[1]}'
    else:
        return f'{parts[0]}/{parts[1]}'

def fix_group(g):
    seq = re.split('[ ,]+', g)
    filtered = [x for x in seq if re.match('[0-9]+/[0-9]+', x)]
    return set([fix_case(c) for c in filtered])

REPEATED = '﻿תיק כפול'
ORIGINAL = 'תיק מקורי'
URL = 'כתובת'
WHAT = 'האם תוצאת התיקים ההמוזגים זהה? (כן- זהה. לא - לא זהה)'
GROUP1 = 'תיקים נוספים שאוחדו ונדחו'
GROUP2 = 'תיקים נוספים שאוחדו והתקבלו'
MULTIPLE= '*/# אם מדובר בריבוי תיקים'
YES ='כן'
NO = 'לא'
allw = set()
P = join(dirname(__file__), 'merged-cases.csv')
result = {'copy':{}, 'copy2': {}, 'to_add': []}
seen = set()
missing = {}
with open(P, 'r', encoding='utf-8') as f:
    for line in csv.DictReader(f):
        what = line[WHAT].strip()
        original = fix_case(line[ORIGINAL])
        repeated = fix_case(line[REPEATED])
        url = line[URL]
        if what == YES:
            result['copy'][repeated] = original
            seen.add(repeated)
        else:
            is_multiple = line[MULTIPLE].strip() in ('#', '*')
            if not is_multiple:
                result['to_add'].append(f'{repeated}:{url}')
                seen.add(repeated)
            else:
                g1 = line[GROUP1].strip()
                g2 = line[GROUP2].strip()
                if not g1 and not g2:
                    if repeated not in seen:
                        missing[repeated] = f'{repeated}:{url}'
                    continue
                g1 = fix_group(g1)
                g2 = fix_group(g2)
                for x in list(g1)+list(g2):
                    if x in missing:
                        del missing[x]
                seen.update(g1)
                seen.update(g2)

                if not g1:
                    print()

                repr1 = min(g1)
                repr2 = min(g2)

                g1.remove(repr1)
                g2.remove(repr2)

                result['to_add'].append(f'{repr1}:{url}')
                result['to_add'].append(f'{repr2}:{url}')

                for x in g1:
                    result['copy2'][x] = repr1
                for x in g2:
                    result['copy2'][x] = repr2

result['to_add'].extend(missing.values())
with open(join(dirname(__file__), 'merged-cases-result.json'), 'w') as f:
    json.dump(result, f, indent=3)


exit(0)