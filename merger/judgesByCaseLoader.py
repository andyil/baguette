
from os.path import dirname, join
import json

_data = join(dirname(__file__), 'judges-by-case2.json')
_data = open(_data, 'r', encoding='utf-8')
_data = json.load(_data)

def get_judges_by_case(case):
    global _data
    r = _data.get(case, None)
    return r

