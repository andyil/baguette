

from os.path import dirname, join
import json
P = join(dirname(dirname(__file__)), 'parser', 'groups.json')


def short_year(c):
    parts = c.split('/')
    return f'{parts[0]}/{parts[1][-2:]}'

def get_copy_spec():
    copy_spec = {}
    merged_to_original = {}
    with open(P, 'r') as f:
        j = json.load(f)
        for k, v in j.items():
            merged = short_year(k)
            original = short_year(v['original'])
            if merged == original:
                continue
            copy_spec.setdefault(original, [])
            copy_spec[original].append(merged)
            merged_to_original[merged] = original

    return copy_spec, merged_to_original

if __name__=="__main__":
    get_copy_spec()

