import os
import re

from datetime import datetime, timedelta

CAN_GPS_SEARCH = r"(\d{4}(?:-\d{2}){5})_(.{17})_(?:CAN|GPS)_Messages?.csv"
ZONE_SEARCH = r"zonefile_(.{17}).json"


def csv_is_empty(filename):
    with open(filename) as f:
        l = f.readline()
        l2 = f.readline()

    return not l or not l2


def round_time(dt, round_to):
    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = (seconds + round_to / 2) // round_to * round_to
    return dt + timedelta(0, rounding - seconds, -dt.microsecond)


def write_files(filepairs, vin, canfile, gpsfile, outputdir, write=True):

    if filepairs:
        if not os.path.isdir(outputdir):
            os.makedirs(outputdir)

        pairnames = []
        for cdata, gdata in filepairs:

            date = datetime.fromtimestamp(cdata.Time.iloc[0]).strftime(
                "%Y-%m-%d-%H-%M-%S"
            )
            name = f"{date}_{vin}_{{}}_Messages.csv"
            can_n = os.path.join(outputdir, name.format("CAN"))
            gps_n = os.path.join(outputdir, name.format("GPS"))
            pairnames.append((os.path.abspath(can_n), os.path.abspath(gps_n)))

            if write:
                cdata.to_csv(can_n, index=False)
                gdata.to_csv(gps_n, index=False)
    else:
        pairnames = []

    print_info(os.path.abspath(canfile), os.path.abspath(gpsfile), pairnames)


def print_info(canfile, gpsfile, pairnames):
    print(f"Input:")
    print(f"    {canfile}")
    print(f"    {gpsfile}")
    print()
    print(f"Output:")
    if pairnames:
        for can, gps in pairnames:
            print(f"    {can}")
            print(f"    {gps}")
    else:
        print(f"    No output.")


def gmt_error_date(canfile, gpsfile):

    with open(canfile, "r") as f:
        f.readline()
        c = f.readline().split(",")[0]

    with open(gpsfile, "r") as f:
        f.readline()
        g = f.readline().split(",")[0]
        while float(g) < 0:  # get first non-negative time to use
            g = f.readline().split(",")[0]

    c = datetime.fromtimestamp(float(c))
    g = datetime.fromtimestamp(float(g))

    diff = round_time(g, 60 * 60) - round_time(c, 60 * 60)

    c = c + diff

    return c.strftime("%Y-%m-%d-%H-%M-%S")


def check_parse_files(canfile, gpsfile, zonesfile):
    can = re.search(CAN_GPS_SEARCH, canfile, re.IGNORECASE)
    gps = re.search(CAN_GPS_SEARCH, gpsfile, re.IGNORECASE)
    zone = re.search(ZONE_SEARCH, zonesfile, re.IGNORECASE)

    if can is None:
        raise ValueError(f"Invalid CAN filename: {canfile}.")
    if gps is None:
        raise ValueError(f"Invalid GPS filename: {gpsfile}.")
    if zone is None:
        raise ValueError(f"Invalid zone filename: {zonesfile}.")

    candate, canvin = can.group(1), can.group(2)
    gpsdate, gpsvin = gps.group(1), gps.group(2)
    zonevin = zone.group(1)

    assert (
        gpsdate == candate
    ), f"Mismatching dates in filenames:\n    GPS  - {gpsdate}\n    CAN  - {candate}"
    assert (
        gpsvin == canvin == zonevin
    ), f"Mismatching vins in filenames:\n    GPS  - {gpsvin}\n    CAN  - {canvin}\n    ZONE - {zonevin}"

    return candate, canvin
