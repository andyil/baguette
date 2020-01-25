from os.path import dirname, join, expanduser, abspath
import json
import csv

def get_missing_cases():
    p = join(dirname(dirname(__file__)), 'parser', 'missing.json')
    f = open(p, 'r')
    j = json.load(f)
    f.close()
    return j

def get_student_answers(reference):
    home = expanduser('~')
    f2 = join(home, 'supreme-court-scrap', 'answers-8.csv')
    f = open(f2, 'r', encoding="utf-8")
    rs = csv.DictReader(f)
    found = {}
    for record in rs:
        casename = record['casename']
        parts = casename.split()
        number = parts[1]
        casenumber, year = tuple(number.split('/'))
        casenumber = int(casenumber)
        year = f'20{year}'
        canonical_case_number = f'{casenumber}/{year}'
        if canonical_case_number in reference:
            found[canonical_case_number] = record

    print(f'found {len(found)}')
    print(f'total {len(reference)}')
    return found

def apply_criteria(case):
    casename = case['casename']
    case_type = casename.split()[0]
    is_bagatz =  case_type in ('בג"ץ', 'בג"צ')
    disposition = case['dispositioncourt']
    outcome = case['outcomecourt']
    has_verdict = disposition == 'On the merits'
    dismissed = outcome == 'Dismissed'
    basic = {'verdict': has_verdict, 'dismissed': dismissed, 'bagatz': is_bagatz}
    if disposition != 'On the merits':
        x = {'action': 'copy', 'reason': 'not on the merits'}
        x.update(basic)
        return x
    if is_bagatz and disposition == 'On the merits' and dismissed:
        x = {'action': 'copy', 'reason': 'bagatz dismissed on the meritz'}
        x.update(basic)
        return x
    x = {'action': 'refeed'}
    x.update(basic)
    return x

filename = 'missing2.csv'
absp = abspath(filename)
f = open(filename, 'w', encoding='utf-8')
columns = ["תיק כפול",
           "תיק מקורי",
           "מצב תיק מקורי בנמלה",
           "כתובת",
           "פסק דין?",
           'בג"ץ?',
           "דחיה על הסף?",
           "פעולה שיש לבצע"]

f.write(','.join(columns))
f.write('\n')
missing = get_missing_cases()

all = list(missing.keys())
for s in missing.values():
    all.extend(s)

answers_by_case = get_student_answers(all)
counts = {}
for original, missing_group in missing.items():

    answered = False
    any = [original] + missing_group
    for the_answered_one in any:
        if the_answered_one in answers_by_case:
            answered = True
            break

    if not answered:
        print(f'{original}, unanswered')
        counts['original-unanswered'] = 1 + counts.setdefault('original-unanswered', 0)

        for missing_case in missing_group:
            row = [missing_case, original, 'ממתין לקידוד']
            f.write(','.join(row))
            f.write('\n')
            counts['unanswered'] = 1 + counts.setdefault('unanswered', 0)

        continue
    original_case = answers_by_case[the_answered_one]
    url = original_case['url']
    criteria = apply_criteria(original_case)
    action ='העתקת  קידוד מהתיק המקורי' if criteria['action'] == 'copy' else 'הוספה לנמלה'
    bagatz ='כן' if criteria['bagatz'] else ''
    dismissed ='כן' if criteria['dismissed'] else ''
    verdict ='כן' if criteria['verdict'] else ''

    for missing_case in missing_group:
        counts[action] = 1 + counts.setdefault(action, 0)
        row = [missing_case, original, 'קודד', url, verdict, bagatz, dismissed, action]
        f.write('%s\n' % ','.join(row))
f.close()
print(counts)
print(f'Wrote to {absp}')
exit(0)