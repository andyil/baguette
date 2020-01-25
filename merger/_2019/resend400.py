import sqlite3

F = r'C:\Users\andy\supreme-court-scrap-Jan2019\db-2019-02-13.sqlite3'

conn = sqlite3.connect(F)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn.row_factory = dict_factory
cases = set()

ids = []
rs = conn.execute('select id from poorslaves_document where metadata like \'%source": "Jan19%\'')
for r in rs:
    ids.append(r['id'])
import random
random.shuffle(ids)

print(f'Got {len(ids)} documents')
resend = ids[:400]
joined = ",".join(map(str,resend))
quoted = f'({joined})'
print(f'update poorslaves_document set answers=0 where id in {quoted};')

