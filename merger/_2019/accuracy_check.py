from os.path import join
from csv import DictReader

F = r'C:\Users\andy\supreme-court-scrap-Jan2019'
F = join(F, 'answers.csv')
F = open(F, 'r', encoding='utf-8')
F = DictReader(F)
reps = {}
for line in F:
    c = line['created']
    if c < '2019':
        continue
    d = line['Document']
    reps.setdefault(d, []).append(line)

two = {}
cols = None
for k, vs in reps.items():
    if len(vs) == 2:
        two[k] = vs
        if not cols:
            for v in vs:
                if 'judge-9' in v:
                    cols = list(v.keys())


OUT = r'C:\Users\andy\supreme-court-scrap-Jan2019\out-acc.csv'
OUT = open(OUT, 'w', encoding='utf-8')
from csv import DictWriter
dw = DictWriter(OUT, fieldnames=cols, lineterminator='\n')
dw.writeheader()
for k, vs in two.items():
    for v in vs:
        dw.writerow(v)
OUT.close()
