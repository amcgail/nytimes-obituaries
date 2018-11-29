from functools import partial

import re
import occ
import nlp
from nlp import HumanName
import numpy as np

coder = occ.Coder()
coder.loadPreviouslyCoded("v2.1")

for obit in coder.obituaries:
    fb = obit['fullBody']

    lines = fb.split("\n")
    lines = filter(lambda x: len(x) > 100, lines)
    some_characters = next(lines)

    if sum( 1 for _ in re.finditer(re.escape(some_characters), fb) ) > 1:
        print("LOOKED FOR ", some_characters)

        print(obit['name'], obit['id'])