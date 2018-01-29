from os.path import join, expanduser
import json

from scrapper.supreme_court import SupremeCourt
output_dir = join(expanduser("~"), "supreme-court")
s = SupremeCourt(output_dir)
ds = s.get_decisions_by_case(2010,1213)
for d in ds:
    pass


exit(0)

