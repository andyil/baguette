
from csv import DictReader
from os.path import dirname, join, exists
from os import makedirs, stat
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request
from time import time

def get_file_by_case(case):
    D = r'C:\Users\andy\supreme-court-scrap\documents-from-student-decoding'
    parts = case.split('/')
    year = parts[-1]
    case = parts[0].zfill(6)
    a, b, c = case[:2], case[2:4], case[4:6]
    dir = join(D, year, a, b)
    outfile = join(dir, f'{c}.html')
    return outfile

def write_out_file(case, text):
    outfile = get_file_by_case(case)
    makedirs(dirname(outfile), 777, True)
    open(outfile, 'w', encoding='Windows-1255').write(text)
    print(f'Wrote to {outfile}')

def parse_case(case):
    url = case['url']
    case_id = case['casename'].split()[1]
    return case_id, url

def exists_case(case_id):
    return exists(get_file_by_case(case_id))

def download(case):
    case_id, url = parse_case(case)
    print(f'Downloading {case_id}')
    s = time()
    response = urllib.request.urlopen(url)
    data = response.read()  # a `bytes` object
    text = data.decode('Windows-1255')  # a `str`; this
    elapsed = time() -s
    print(f'Downloaded {case_id} in {elapsed}')
    write_out_file(case_id, text)
    return

f = r'C:\Users\andy\supreme-court-scrap\answers-13.csv'
f = open(f, 'r', encoding='utf-8')
f = DictReader(f)
futures = []

with ThreadPoolExecutor(max_workers=20) as tpe:
    for case in f:
        case_id, url = parse_case(case)
        if exists_case(case_id):
            print(f'Skipping {case_id}')
            continue

        future = tpe.submit(download, case)
        futures.append(future)

    for future in as_completed(futures):
        future.result()
