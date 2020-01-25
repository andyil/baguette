from os.path import join
from csv import DictReader

D=r'C:\Users\andy\supreme-court-scrap-Jan2019'
D = join(D, 'answers-2.csv')

by_doc = {}
print('first pass')
with open(D, 'r', encoding='utf-8') as f:
    for line in DictReader(f):
        if line['created'] < '2019-02-13':
            continue
        doc = line['Document']
        by_doc.setdefault(doc, [])

print('second pass')
with open(D, 'r', encoding='utf-8') as f:
    for line in DictReader(f):
        doc = line['Document']
        if doc in by_doc:
            by_doc[doc].append(line)

baddocs = set()
variables = ['dispositioncourt', 'outcomecourt', 'winnercourt']
judges = [f'judge-{i}' for i in range(0, 10)]
reason = {'judge': 0}
for v in variables:
    reason[v] = 0
for doc, lines in by_doc.items():
    for v in variables:
        results = set([line[v] for line in lines])
        if len(results) > 1:
            print(f'doc {doc} has {len(results)} {v}')
            baddocs.add(doc)
            reason[v] += 1

    judges1 = set([lines[0].get(j, None) for j in judges if j in lines[0] and lines[0][j]])
    for line in lines[1:]:
        judges2 = set([line.get(j, None) for j in judges if j in line and line[j]])

        if judges1 != judges2 or len(judges1) % 2 == 0 or len(judges2) % 2 == 0:
            reason['judge'] += 1


print(f'total resend {len(baddocs)} out of {len(by_doc)}')
print(reason)

ids = ",".join(baddocs)
print (f'update poorslaves_document set answers=0 where id in ({ids})')

