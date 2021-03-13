import os
import regex as re
import sys

from datetime import datetime, timedelta

CAN_GPS_SEARCH = r"(\d{4}(?:-\d{2}){5})_(.{17})_(?:CAN|GPS)_Messages?.csv"
ZONE_SEARCH = r"zonefile_(.{17}).json"


def csv_is_empty(filename):
    with open(filename) as f:
        l = f.readline()
        l2 = f.readline()

    if not l or not l2:
        return True
    else:
        return False


def round_time(dt, round_to):
    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = (seconds + round_to / 2) // round_to * round_to
    return dt + timedelta(0, rounding - seconds, -dt.microsecond)


def get_zonesfile(canfile):
    raise NotImplementedError("Currently must provide a zonefile with -z flag.")


def write_files(filepairs, vin, outputdir, empty=None):

    for cdata, gdata in filepairs:

        if not empty:
            date = datetime.fromtimestamp(cdata.Time.iloc[0]).strftime(
                "%Y-%m-%d-%H-%M-%S"
            )
            name = f"{date}_{vin}_{{}}_Messages.csv"
            cdata.to_csv(os.path.join(outputdir, name.format("CAN")), index=False)
            gdata.to_csv(os.path.join(outputdir, name.format("GPS")), index=False)
        else:
            date = empty
            name = f"{date}_{vin}_{{}}_Messages.csv"

            with open(os.path.join(outputdir, name.format("CAN")), "w") as fw, open(
                cdata
            ) as fr:
                fw.write(fr.read())

            with open(os.path.join(outputdir, name.format("GPS")), "w") as fw, open(
                gdata
            ) as fr:
                fw.write(fr.read())


def write_error(err_date, vin, err, outputdir):

    name = f"{err_date}_{vin}_ERROR.txt"

    filepath = os.path.join(outputdir, name)

    with open(filepath, "w") as f:
        f.write(err)

    print(f"Encountered an error during proccesing.\nSaved error file as {filepath}.")


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
