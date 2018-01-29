import argparse
from os.path import join, expanduser

from scrapper.supreme_court import SupremeCourt
from scrapper.DaysSpan import DaysSpan

parser = argparse.ArgumentParser(description='Scraps the website of Israel\'s Supreme Court')
parser.add_argument("-o", "--output-dir", nargs=1, default=join(expanduser("~"), "supreme-court"))
parser.add_argument("-d", "--days", nargs=1)
parser.add_argument("--dry", action="store_true", default=False)


parsed_args = parser.parse_args()

output_dir = parsed_args.output_dir
print parsed_args.days
days = DaysSpan(parsed_args.days[0]).days

dry_run = parsed_args.dry

if dry_run:
    print "Going to scrap %s days: %s" % (len(days), ", ".join((map(str, days))))
    print "Going to store output in %s" % output_dir
    print "Just a dry run, doing nothing this time"
    exit(0)
s = SupremeCourt(output_dir)
print "Output directory is %s" % output_dir
for d in days:
    print "Scrapping day %s" % d
    s.get_decisions_by_day_case_opened(d)
s.close()
exit(0)

