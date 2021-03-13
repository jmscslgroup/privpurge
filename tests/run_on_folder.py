import itertools
import os
import regex as re

import privpurge

CAN_GPS_SEARCH = r"(.*)((?:CAN|GPS)_Messages?.csv)"

VIN_SEARCH = r".*_(.{17})_(?:CAN|GPS)_Messages?.csv"


def run_folder(folder, output):

    folder = os.path.join(os.getcwd(), folder)
    output = os.path.join(os.getcwd(), output)

    files = [a for a in os.listdir(folder) if os.path.isfile(os.path.join(folder, a))]

    res = []
    for f in files:
        m = re.search(CAN_GPS_SEARCH, f, re.IGNORECASE)
        if m:
            res.append((m.group(1), m.group(2)))

    res = [list(l) for k, l in itertools.groupby(res, lambda x: x[0])]
    res = sorted(res, key=lambda x: x[1])
    res = [("".join(a), "".join(b)) for a, b in res]

    for c, g in res:
        print(c, g)
        vin = re.search(VIN_SEARCH, c, re.IGNORECASE).group(1)
        privpurge.run(
            os.path.join(folder, c),
            os.path.join(folder, g),
            output,
            os.path.join(folder, f"zonefile_{vin}.json"),
        )


import sys

if len(sys.argv[1:]) > 2:
    print("pass only input folder and output folder")
else:
    run_folder(sys.argv[1:])
