import argparse
from os.path import join, expanduser, abspath
from scrapper.DaysSpan import DaysSpan
from scrapper.supreme_court import SupremeCourtScrapper
import multiprocessing
from os import getpid

def pool_initialize(output_dir):
    global scrapper
    scrapper = SupremeCourtScrapper(output_dir)
    print(f'[{getpid()}] Initialized')

def pool_scrap_day(day):
    global scrapper
    print(f'[{getpid()}] Starting {day}')
    scrapper.get_decisions_by_day_case_opened(day)
    print(f'[{getpid()}] Finished {day}')


def main():
    parser = argparse.ArgumentParser(description='Scraps the website of Israel\'s Supreme Court')
    parser.add_argument("-o", "--output-dir", default=join(expanduser("~"), "supreme-court"))
    parser.add_argument("-d", "--days", nargs=1)
    parser.add_argument("--dry", action="store_true", default=False)
    parser.add_argument('-p', '--parallel', default=1, required=False, type=int)

    parsed_args = parser.parse_args()

    output_dir = abspath(parsed_args.output_dir)
    days = DaysSpan(parsed_args.days[0]).days

    parallel = parsed_args.parallel
    dry_run = parsed_args.dry

    if dry_run:
        print(f'Going to scrap {len(days)} days, first {days[0]}, last {days[-1]}')
        print(f'Going to store output in {output_dir}')
        print(f'Parallelism {parallel}')
        print()
        print("Just a dry run, doing nothing this time")
        exit(0)


    print ("Output directory is %s" % output_dir)
    results = []
    with multiprocessing.Pool(parallel, pool_initialize, (output_dir,)) as p:
        r = p.map(pool_scrap_day, days)

    print(r)


    exit(0)

if __name__=='__main__':
    main()

