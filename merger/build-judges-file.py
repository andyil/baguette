from os.path import join, dirname
import json
import re

path = r'C:\Users\andy\supreme-court-scrap\document-hashes'
filename = join(path, 'writers-by-text-3.txt')

judge_metadata = join(dirname(__file__), 'judge-metadata.json')
judge_metadata = open(judge_metadata, 'r', encoding='utf-8')
judge_metadata = json.load(judge_metadata)


def get_title(s):
    if 'שופט' in s:
        return 'judge'
    if 'משנה לנשיא' in s or 'משנה-לנשיא' in s:
        return 'vice president'
    if 'משנָה לנשיא' in s:
        return 'vice president'
    if 'הנשיא' in s:
        return 'president'
    raise Exception('unknown')

def is_retired(s):
    return 'דימוס' in s or 'דימ\'' in s or 'דימ \'' in s or 'בדימ)' in s

def parse(s):
    retired = is_retired(s)
    title = get_title(s)
    s = re.sub('\s+', ' ', s)
    s = re.sub('[(].*[)]', '', s)
    s = re.sub('\s[\']', '\'', s)
    s = re.sub('\s(\S)\s', ' \\1\' ', s)
    s = re.sub('\s(\S)[.]', ' \\1\'', s)

    if "'" not in s:
        n = s.split()[-1]
    else:
        n = s[s.index("'")-1:]
    m = judge_metadata[n]
    if 'ref' in m:
        m = judge_metadata[m['ref']]
    if 'english' not in m:
        raise Exception()
    return {m['english']:  {'retired': retired, 'title': title}}



with open(filename, 'r', encoding='utf-8') as f:
    m = {}
    for line in f:
        record = {}
        j = json.loads(line)
        case = j['case_id']

        by_judge = {}

        for w in j['all']:
            parsed = parse(w)
            by_judge.update(parsed)
        record['judges'] = by_judge
        if j['writer']:
            parsed = parse(j['writer'])
            record['writer'] = list(parsed.keys())[0]
        m[case] = record

outfile = join(dirname(__file__), 'judges-by-case2.json')
json.dump(m, open(outfile, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
exit(0)

