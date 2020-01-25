from os.path import join, expanduser
import csv
import json

def get_scrapped_cases():
    SCRAP_OUTPUT_PATH = join(expanduser('~'), "supreme-court-scrap", "out", "54456")
    f1 = join(SCRAP_OUTPUT_PATH, 'cases.csv')
    f = open(f1, 'r', encoding="utf-8")
    r = csv.DictReader(f, delimiter='\t')

    all_cases = {}
    for line in r:
        case = line['caseId']
        all_cases[case] = line
    return all_cases

def get_stud_cases():
    home = expanduser('~')
    f2 = join(home, 'supreme-court-scrap', 'answers-21.csv')

    f = open(f2, 'r', encoding="utf-8")
    r = csv.DictReader(f)
    all_cases = {}
    for line in r:
        nn = line['casename'].split()[1]
        all_cases[nn] = line
    return all_cases

def num_just(scrapped):
    return len(set([scrapped['justice%s' % i] for i in range(1,10) if scrapped['justice%s' % i].strip()] ))

def explain_missing(scrapped, students):
    f = open("missing-2018-12-17.csv", 'w', encoding='utf-8')
    to_add = {'to_add': []}
    badly = 0
    f.write(f'תיקים חסרים')
    f.write('\n')
    for s in scrapped:
        if s in students:
            continue
        missing_case = scrapped[s]
        n = num_just(missing_case)
        if n < 3:
            continue
        proc = missing_case['legalProcedureHebrew']
        badly += 1
        print(s+" "+proc)
        filepath = missing_case['file_path']
        filename = missing_case['file_name']
        url = f'https://supremedecisions.court.gov.il/Home/Download?path={filepath}&fileName={filename}&type=2'
        print(url)
        case_n = s.split('/')[0]
        year = f'20{s.split("/")[1]}'
        to_add['to_add'].append(f'{case_n}/{year}:{url}')
        f.write(s+' '+proc+","+str(n))
        f.write('\n')
    print(f'{badly}')
    f.close()
    f = open('missing-2018-12-17.json', 'w', encoding='utf-8')
    f.write(json.dumps(to_add))
    f.close()

students = get_stud_cases()
scrapped = get_scrapped_cases()
print(f'Scrapped {len(scrapped)}')
print(f'students {len(students)}')
explain_missing(scrapped, students)