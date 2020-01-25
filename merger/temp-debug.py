import csv
import json

p = r'C:\Users\andy\supreme-court-scrap\answers-7.csv'


def bad_agreed_outcome():
    r= csv.DictReader(open(p, 'r', encoding='utf-8'))
    badones = '7385/13', '1877/14', '3752/10', '3660/17'
    for line in r:
        for b in badones:
            if b in line['casename']:
                print(f'{b}   {json.dumps(line)}')


def no_match():
    r= csv.DictReader(open(p, 'r', encoding='utf-8'))
    badones = ('7703/10',)
    for line in r:
        for b in badones:
            if b in line['casename']:
                print(f'{b}   {json.dumps(line)}')

def count_judges(line):
    judges = [line.get('judge-%s' % i, '') for i in range(1, 10)]
    judges = [j for j in judges if j]
    return judges

def four_judges():
    r= csv.DictReader(open(p, 'r', encoding='utf-8'))
    fucked = []
    fixed = []
    even = []
    for line in r:
        judges = count_judges(line)
        if len(judges) % 2 == 0:
            print(f'{line["casename"]} is fucked {len(judges)}')
            fucked.append(line['casename'])
            if len(set(judges)) %2 == 1:
                even.append(line['casename'])
                print('EVEN AFTER ALL')

        else:
            if line['casename'] in fucked:
                print(f'{line["casename"]} FIXED ITSELF!!!')
                fixed.append(line['casename'])

    even = [x for x in even if x not in fixed]
    for e in even:
        print(f'EVEN {e}')
    print(f'{len(even)} EVEN')
    fucked = list(set(fucked))
    rfucked = [e.split()[1] for e in fucked]
    for e in fucked:
        print(f'FUCKED {e.split()[1]}')
    print(", ".join(rfucked))
    print(f'{len(fucked)} FUCKED')

    for e in fixed:
        print(f'FIXED {e}')
    print(f'{len(fixed)} FIXED')
    the_fixed = [e.split()[1] for e in fixed]
    print(", ".join(the_fixed))

    afterall = set(fucked) - set(fixed) - set(even)
    for a in afterall:
        print(f'AFTER ALL {a}')
    print(len(afterall))
    the_afterall = [e.split()[1] for e in afterall]
    print(", ".join(the_afterall))


no_match()
exit()
four_judges()
exit()
bad_agreed_outcome()