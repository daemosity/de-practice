import sys

import pandas as pd

print(sys.argv)

day = sys.argv[1]
# sys.argv[0] is name of the file
# sys.argv[1] is whatever is passed to the file

# some fancy stuff with pandas

print(f'job completed successfully for day = {day}')