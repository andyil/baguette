from os.path import expanduser, dirname, join
import csv
from collections import OrderedDict
from os.path import join
from baguette.merger import fields_fixer
from baguette.merger.fields_order import fields as ordered_fields, fields_judges
from baguette.parser.Groups import groups
from baguette.merger import side_types
from baguette.merger import translate_justice
from baguette.merger.loadCopySpecs import get_copy_spec
from baguette.merger.copyfields import copy_fields
from baguette.merger.judgesByCaseLoader import get_judges_by_case
from baguette.merger.default_student_encoding_fixer import fix_default_student_encoding, print_report
import re
import json
from time import time
import traceback

SCRAP_OUTPUT_PATH=join(expanduser('~'), "supreme-court-scrap", "out", "54456")

uninteresting_cases = json.load(open(join(dirname(__file__), 'uninteresting-cases.json'), 'r', encoding='utf-8'))
uninteresting_cases = set(uninteresting_cases)

copy_spec, merged_to_original = get_copy_spec()
big_bad = {}

def clean_dict(d):
    r = OrderedDict()
    for k, v in d.items():
        k = k.strip().replace(chr(65279), '')
        r[k] = v
    return r

def get_cases():
    f1 = join(SCRAP_OUTPUT_PATH, 'cases.csv')
    f = open(f1, 'r', encoding="utf-8")
    r = csv.DictReader(f, delimiter='\t')

    missing = open(r'C:\Users\andy\baguette\baguette\missing\missing.json', 'r')
    missing = json.loads(missing.read())

    all_cases = {}
    for line in r:
        case = line['caseId']
        line = clean_dict(line)
        if case in missing:
            missing_case = missing[case]
            line['Nwords'] = str(missing_case['words'])
            line['Njudges'] = str(missing_case['judges'])
            line['dateFinalDecision'] = missing_case['last_decision']
        all_cases[case] = line

    f.close()
    return all_cases

def get_judges():
    f1 = join(SCRAP_OUTPUT_PATH, 'judges.csv')
    f = open(f1, 'r', encoding="utf-8")
    r = csv.DictReader(f, delimiter='\t')

    all_cases = {}
    for line in r:
        case = line['caseId']
        name = line['Name']
        key = "%s,%s" % (case, name)
        all_cases[key] = clean_dict(line)
    f.close()
    return all_cases

def is_common_field(f):
    return f in ['Document', 'person', 'casename', 'url']

def is_court_field(f):
    return is_common_field(f) or 'court' in f or f.startswith('judge-')

def extract_case_n(d):
    case = d['casename']
    case_n = case.split()[1]
    while case_n[0] == '0':
        case_n = case_n[1:]
    return case_n

def is_judge_field(f, i):
    import re
    return is_common_field(f) or (re.match('[a-z]+-%s' % i, f) and 'court' not in f)

def check_judges_problem(line):
    all_judges = [line.get('judge-%s' % i, '') for i in range(1, 10)
                        if line.get('judge-%s' % i, '')]
    if len(all_judges) % 2 == 0:
        return 'even'
    unique = set()
    for j in all_judges:
        if j in unique:
            return f'repeated {j}'
    return None


def fix_bagatz_lower_instance(x):
    if x['legalProcedure'] != 'High Court of Justice':
        return None
    rns = [f'respondent{i}' for i in range(1,4)]
    beit_din = ["בית הדין", "בית דין", "בי\"ד", "ביה\"ד", 'בית משפט', 'בית המשפט', 'שופט']
    work_court = ['אזורי לעבודה', 'ארצי לעבודה']
    religions_court = ['נוצרי','רבני','שרעי','כנסיתי','כנסייתי','דרוזי','לגיור']
    pairs = [(x,y,'Labor Court') for x in work_court for y in beit_din]
    pairs.extend( [(x,y,'Religious court') for x in religions_court for y in beit_din])
    military = ['צבא']
    pairs.extend( [(x,y,'Military Court') for x in military for y in beit_din])

    for rn in rns:
        r = x[rn]
        for a1, a2, result in pairs:
            if a1 in r and a2 in r:
                return result
    return None


def get_judges_by_case_grouped(case):
    g = get_judges_by_case(case)
    if g:
        return g
    parts = case.split('/')
    for_groups = f'{parts[0]}/20{parts[1]}'
    if for_groups in groups:
        original = groups[for_groups]['original']
        original = re.sub('/20', '/', original)
        g = get_judges_by_case(original)
        return g
    return None

def delete_attributes(r):
    for a in ['agreedOutcome', 'nMajority', 'nMinority']:
        if a in r:
            del r[a]

def fix_issues(line):

    if line['caseId'] == '6321/14':
        line['caseCitation'] = r"""בג"ץ 6321/14 כן לזקן - לקידום זכויות הזקני נ' שר האוצר"""
        line['casename'] = r"""כן לזקן - לקידום זכויות הזקני נ' שר האוצר"""
        line['lawyerR3'] = ''
        line['NPetitioners'] = '7'
        line['NRespondents'] = '3'
    if line['caseId'] == '5380/11':
        line['LIssue'] = 'Administrative Law'
    if line['caseId'] == '8343/12':
        line['issuecourt-1'] = 'National security, military, and the territories'
    if line['caseId'] == '3106/10':
        line['issuecourt-1'] = 'Civil - Torts'
    if line['caseId'] == '7470/13':
        line['dateFinalDecision'] = '22/2/2016'
        if 'Seniority' in line and str(line['Seniority']) == '-1':
            line['Seniority'] = '0'

    n = {}
    fields_to_delete = set()
    for k, v in line.items():
        if type(v) == str and 'issue' in k and 'מכרזים' in v:
            v = v.replace('מכרזים', '').strip()
            line[k] = v
        if k == 'issue-1':
            n['issue1Justice'] = v
            fields_to_delete.add(k)
        elif k == 'issue-2':
            n['issue2Justice'] = v
            fields_to_delete.add(k)
        elif k in ('outcome', 'disposition', 'winner', 'dissent'):
            n[f'{k}Justice'] = v
            fields_to_delete.add(k)

    for f in fields_to_delete:
        del line[f]
    line.update(n)

def get_stud_coding_court(courtonly):
    home = expanduser('~')

    f2 = join(home, 'supreme-court-scrap', 'answers-21.csv')

    f = open(f2, 'r', encoding="utf-8")
    r = csv.DictReader(f)

    all_cases = {}
    for line in r:
        nl = OrderedDict()
        line = clean_dict(line)
        issue = check_judges_problem(line)
        if issue:
            nn = line['casename'].split()[1]
            big_bad[nn] = issue

            continue
        fix_default_student_encoding(line)
        for k, v in line.items():
            if not courtonly or is_court_field(k):
                nl[k] = v
        case_n = extract_case_n(nl)
        all_cases[case_n] = nl
    f.close()
    for case in all_cases.keys():
        if case in big_bad:
            del big_bad[case]
    print(f'{len(big_bad)} all even {", ".join(list(big_bad.keys())[:10])}')
    print_report()
    return all_cases

def full_judge_data(n, case_n):
    by_case = get_judges_by_case_grouped(case_n)
    r = translate_justice.translate_judge(n, True)
    if by_case:
        name = {k: v for k, v in r}['Name']
        if name in by_case['judges']:
            extra = by_case['judges'][name]
            r.append(('Retired', "Retired" if extra['retired'] else "Presiding"))
            r.append(('Title', extra['title']))
        else:
            big_bad[case_n] = f'check judge {name}'
    return r


def fix_field(k, v, case=None):
    attr_name = f'fix_{k}'

    if k.startswith('justice'):
        return None

    if k=='jOpinionWriter':
        by_case = get_judges_by_case_grouped(case)
        if not by_case or 'writer' not in by_case:
            return [('jOpinionWriter', '')]
        writer = by_case['writer']

        return [('jOpinionWriter', writer)]

    if k.startswith('judge-') or k=='Name':
        translated = translate_justice.translate_judge(v)
        return k.replace('judge-', 'justice'), translated

    if k.startswith('petitioner') or k.startswith('respondent'):
        sidetype = side_types.get_side_type(v)
        new_field = k.replace('petitioner', 'petitionerType')
        new_field = new_field.replace('respondent', 'respondentType')
        return [(k, v), (new_field, sidetype)]

    if hasattr(fields_fixer, attr_name):
        f = getattr(fields_fixer, attr_name)
        return f(v)
    return k, v

def iscd_id(das):
    caseId = das['caseId']
    parts = caseId.split('/')
    first = parts[1]
    second = parts[0].zfill(5)
    return f'{first}{second}'

def get_groups(das):
    caseId = das['caseId']
    parts = caseId.split('/')
    yr = f'20{parts[1]}'
    n = parts[0]
    k = f'{n}/{yr}'
    if k not in groups:
        return "", ""
    v = groups[k]
    if v["cases"] == 1:
        return "", ""
    original_number = v['original'].split('/')[0]
    yr = v['original'][-2:]
    return f'{original_number}/{yr}', v['cases']

def getAgreedOutcome(students):
    judges = []
    for ii in range(1, 10):
        judge = students['judge-%s' % ii]
        if judge:
            judges.append(judge)
        else:
            break
    results = {}
    count = {}
    seen_judges = set()
    discent = set()
    courtResult = students['outcomecourt']+":"+students['winnercourt']
    for i, j in enumerate(judges):
        if j in seen_judges:
            continue
        seen_judges.add(j)
        ii = i+1
        result = students['outcome-%s' % ii]+":"+students['winner-%s' % ii]
        count[result] = 1 + count.setdefault(result, 0)
        results[j] = result
        if results[j] != courtResult:
            discent.add(j)

    nMajority = max(count.values())
    numberOfJudges = len(set(judges))
    nMinority = numberOfJudges - nMajority
    if nMinority >= nMajority or nMinority < 0:
        print('Less majority than minority')
        print(f'nMinority {nMinority} nMajority {nMajority} judges {numberOfJudges}')
    type = 'unanimous' if nMinority == 0 else 'split'
    return nMajority, nMinority,  type, discent, numberOfJudges

def copy_fields_from_merged(scrapped, all):
    case, number = get_groups(scrapped)
    if not case:
        return
    if number == 1:
        return
    originalCase = scrapped['caseId']
    if case == originalCase:
        return
    if case not in all:
        return
    original = all[case]
    for f in copy_fields:
        if f not in original or (f in scrapped and str(scrapped[f]).strip()):
            continue
        scrapped[f] = original[f]
    return

cases_written = set()
def one_case(dict_writer, scrapped_cases, k, v, original_case_n=None):
    global cases_written, merged_to_original
    if k in cases_written:
        return
    if k not in scrapped_cases:
        if k not in uninteresting_cases:
            big_bad[k] = 'probably confidential?'
        return
    try:
        scrappedRow = scrapped_cases[k]

        if original_case_n is None and k in merged_to_original:
            original_case_n = merged_to_original[k]

        if original_case_n and original_case_n in scrapped_cases:
            original_case = scrapped_cases[original_case_n]
            for f in ['Njudges', 'Nwords', 'dateFinalDecision']:
                if f not in scrappedRow or not scrappedRow[f]:
                    scrappedRow[f] = original_case[f]

        row = OrderedDict()

        nMajority, nMinority, agreedOutcome, dissent, numberOfJudges = getAgreedOutcome(v)
        row['nMajority'] = nMajority
        row['nMinority'] = nMinority
        row['agreedOutcome'] = agreedOutcome
        delete_attributes(scrappedRow)
        v2 = {k: v for k, v in v.items() if is_court_field(k)}
        for k1, v1 in list(v2.items()) + list(scrappedRow.items()):
            if v1 is None:
                v1 = ''
            fixed = fix_field(k1, v1.strip(), case=k)
            if fixed is None:
                continue
            if type(fixed) == tuple:
                fixed_k, fixed_v = fixed
                row[fixed_k] = fixed_v
            if type(fixed) == list:
                for fixed_k, fixed_v in fixed:
                    row[fixed_k] = fixed_v
        row['ISCD_ID'] = iscd_id(scrappedRow)
        row['merged_first'], row['merged'] = get_groups(scrappedRow)
        if not row['courtSourceInstance']:
            lower = fix_bagatz_lower_instance(scrappedRow)
            if lower:
                row['courtSourceInstance'] = lower

        row['Njudges'] = numberOfJudges
        fix_issues(row)
        dict_writer.writerow(row)
        cases_written.add(k)

    except Exception as e:
        print(f'Bad Case! {k}')
        traceback.print_exc()
        return

def merge_cases(s, scrapped_cases):
    home = expanduser('~')
    csvfile = open(join(home, 'supreme-court-merge', 'cases.csv'), 'w', encoding="utf-8")
    dict_writer = csv.DictWriter(csvfile, extrasaction='ignore', fieldnames=ordered_fields, lineterminator="\n")
    dict_writer.writeheader()
    before = len(big_bad)
    debt = {}
    for k, v in s.items():
        one_case(dict_writer, scrapped_cases, k, v)
        if k in copy_spec:
            for c in copy_spec[k]:
                debt[c] = k, v

    for k, pair in debt.items():
        original_case_n, original_case = pair
        one_case(dict_writer, scrapped_cases, k, original_case, original_case_n)

    csvfile.close()
    problematic = len(big_bad) - before
    print(f'Total Cases {len(s)}, Missing {problematic}')


def unfold(sj):
    unfolded = {}
    for k,v in sj.items():
        case_n = extract_case_n(v)
        judges = {'judge-%s' % i : v['judge-%s' % i] for i in range(1, 10)
                  if v['judge-%s' % i]}
        for i, j in enumerate(judges.values()):
            judge_n = i + 1
            by_judge = OrderedDict()
            for field, value in v.items():
                if is_judge_field(field, judge_n):
                    by_judge[field_to_1(field)] = value
                elif 'court' in field:
                    by_judge[field] = value

            by_judge.update(judges)

            if case_n not in unfolded:
                unfolded[case_n] = {'by_judge': OrderedDict(), 'original': v}
            unfolded[case_n]['by_judge'][j] = by_judge

    return unfolded

def field_to_1(o):
    import re
    f = re.sub('([a-z]+)-[0-9]', '\\1', o)
    return f

cases_judges_seen = set()
def one_case_judges(missing, dict_writer, stud, scrapped, case_n, v, original_case_n = None):
    rows = 0
    curr_iscd_id = ''
    if case_n in cases_judges_seen:
        return 0
    try:
        if case_n not in scrapped:
            missing.add(case_n)
            return 0
        from_scrap = scrapped[case_n]

        copy_fields_from_merged(from_scrap, scrapped)

        if original_case_n and original_case_n in scrapped:
            original_case = scrapped[original_case_n]
            for f in ['Njudges', 'Nwords', 'dateFinalDecision']:
                if f not in from_scrap or not from_scrap[f]:
                    from_scrap[f] = original_case[f]

        by_judge = v['by_judge']
        for judge, case in by_judge.items():

            row = OrderedDict()
            if case_n in stud:
                original_stud = stud[case_n]
            else:
                original_stud = stud[original_case_n]
            nMajority, nMinority, agreedOutcome, dissent, numberOfJudges = getAgreedOutcome(original_stud['original'])
            row['nMajority'] = nMajority
            row['nMinority'] = nMinority
            row['agreedOutcome'] = agreedOutcome
            delete_attributes(from_scrap)
            if judge in dissent:
                row['dissent'] = 'Dissenting'
            else:
                row['dissent'] = 'Not dissenting'

            judge_metadata = full_judge_data(judge, case_n)
            for judge_metadata_k, judge_metadata_v in judge_metadata:
                if judge_metadata_k != 'Year':
                    row[judge_metadata_k] = judge_metadata_v
                else:
                    finalDecisionDate = from_scrap['dateFinalDecision']
                    if finalDecisionDate:
                        parts = finalDecisionDate.split('-')
                        finalDecisionYear = int(parts[0])
                        if case_n == '6321/14':
                            finalDecisionYear = 2017
                        row['Seniority'] = finalDecisionYear - int(judge_metadata_v)
                    else:
                        row['Seniority'] = ''

            for k1, v1 in list(from_scrap.items()) + list(case.items()):
                v1 = v1 or ''
                fixed = fix_field(k1, v1.strip(), case=case_n)
                if fixed is None:
                    continue
                if type(fixed) == tuple:
                    fixed_k, fixed_v = fixed
                    row[fixed_k] = fixed_v
                if type(fixed) == list:
                    for fixed_k, fixed_v in fixed:
                        row[fixed_k] = fixed_v
            ISCD_ID = iscd_id(from_scrap)
            if ISCD_ID == curr_iscd_id:
                number += 1
            else:
                curr_iscd_id = ISCD_ID
                number = 1
            row['ISCD_ID'] = f'{ISCD_ID}.{str(number).zfill(2)}'
            row['merged_first'], row['merged'] = get_groups(from_scrap)

            if not row['courtSourceInstance']:
                lower = fix_bagatz_lower_instance(from_scrap)
                if lower:
                    row['courtSourceInstance'] = lower

            cases_judges_seen.add(case_n)
            row['Njudges'] = numberOfJudges
            fix_issues(row)
            dict_writer.writerow(row)
            rows += 1
        return rows
    except Exception as e:
        print(f'Bad judge! {case_n}')
        traceback.print_exc()
        return rows

def merge_judges(stud, scrapped):
    missing = set()
    home = expanduser('~')
    csvfile = open(join(home, 'supreme-court-merge', 'judges.csv'), 'w', encoding="utf-8")

    dict_writer = csv.DictWriter(csvfile, extrasaction='ignore', fieldnames=fields_judges,
                                 lineterminator="\n")
    dict_writer.writeheader()

    rows = 0
    debt = {}
    for case_n, v in stud.items():

        rows += one_case_judges(missing, dict_writer, stud, scrapped, case_n, v)

        if case_n in copy_spec:
            for c in copy_spec[case_n]:
                debt[c] = case_n, v

    for k, pair in debt.items():
        original_case_n, v = pair
        rows += one_case_judges(missing, dict_writer, stud, scrapped, k, v, original_case_n)


    csvfile.close()
    print(list(missing)[:10])
    print(f'Total judges {len(stud)}, Missing {len(missing)}, Rows {rows}')

def cases(sc):
    c = get_cases()
    merge_cases(sc, c)

def judges(sc):
    sc = unfold(sc)
    j = get_cases()
    merge_judges(sc, j)

def write_bad():
    home = expanduser('~')
    csvfile = open(join(home, 'supreme-court-merge', 'bad-cases.csv'), 'w', encoding="utf-8")
    csvfile.write('case number, issue\n')
    for k, v in big_bad.items():
        csvfile.write(f'{k},{v}\n')
    csvfile.close()


def main():
    s = time()
    sc = get_stud_coding_court(courtonly=False)
    judges(sc)
    cases(sc)
    elapsed = int(time() - s)

    print(f'In {elapsed} sec. Output in {join(expanduser("~"), "supreme-court-merge")}')
    print(f'Problematic {len(big_bad)}')
    write_bad()


if __name__=="__main__":
    main()


