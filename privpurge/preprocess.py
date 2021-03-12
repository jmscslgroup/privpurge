import os
import pandas
import json
import itertools

from datetime import datetime
from dateutil import tz
import pytz

from .utils import round_time


def standardize_time(candata, gpsdata):

    c_one = datetime.fromtimestamp(candata.Time.iloc[0])
    g_one = datetime.fromtimestamp(gpsdata.Gpstime.iloc[0])  # gpstime in UTC

    diff = round_time(g_one, 60 * 60) - round_time(c_one, 60 * 60)

    candata.Time = [
        (datetime.fromtimestamp(c) + diff).timestamp() for c in candata.Time
    ]  # convert can time to gmt (gmt = utc+0)

    return candata, gpsdata


def fix_gps(gpsdata):  # remove until consecutive negatives stop

    temp = [
        list(g)
        for k, g in itertools.groupby(gpsdata.Gpstime, lambda x: -1 if x < 0 else 1)
    ]
    if temp[-1][0] < 0:
        raise ValueError(
            "Error found in gpsfile. Last grouped list has negative times."
        )
    elif len(temp) > 3:
        raise ValueError(
            "Error found in gpsfile. Length of grouped list is greater than three, interspersed negatives."
        )

    temp = sum([[True if i > 0 else False for i in l] for l in temp], start=[])

    gpsdata = gpsdata[temp]

    return gpsdata


def preprocess(canfile, gpsfile, outdir, zonesfile):

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    candata = pandas.read_csv(canfile)
    gpsdata = pandas.read_csv(gpsfile)
    with open(zonesfile, "r") as f:
        zones = json.load(f)

    gpsdata = fix_gps(gpsdata)
    candata, gpsdata = standardize_time(candata, gpsdata)

    return candata, gpsdata, zones
