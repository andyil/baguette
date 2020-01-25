from os.path import join, dirname
import json

def load_metadata():
    f = join(dirname(__file__), 'judge-metadata.json')
    file = open(f, 'r', encoding='utf-8')
    j = json.load(file)
    file.close()
    return j

judge_metadata = load_metadata()
seen_missing = set()

def translate_judge(j, with_metadata=False):
    if not j.strip():
        return ''
    global judge_metadata, seen_missing
    if j not in judge_metadata:
        if j not in seen_missing:
            print(f'missing judge {j}')
        seen_missing.add(j)
        return j

    entry = judge_metadata[j]
    if 'ref' in entry:
        return translate_judge(entry['ref'], with_metadata)

    if not with_metadata:
        return entry['english']
    else:
        return [
            ('Name', entry['english']),
            ('Experience', entry['previous']),
            ('Gender', entry['sex']),
            ('Religion', entry['religion']),
            ('Year', entry['since'])
            ]
