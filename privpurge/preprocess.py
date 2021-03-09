import os
import pandas
import json

from datetime import datetime, timedelta
from dateutil import tz
import pytz


def make_gmt(candata, gpsdata):

    c_one = datetime.fromtimestamp(candata.Time.iloc[0])
    g_one = datetime.fromtimestamp(gpsdata.Gpstime.iloc[0])

    temp = g_one - c_one
    if 25000 <= temp.seconds <= 25400:
        r = timedelta(hours=-7)
    else:
        raise NotImplementedError

    candata.Time = [(datetime.fromtimestamp(c) + r).timestamp() for c in candata.Time]
    # gpsdata.Gpstime = [(datetime.fromtimestamp(g) + r).timestamp() for g in gpsdata.Gpstime]

    return candata, gpsdata


def fix_gps(gpsdata):  # remove until consecutive negatives stop

    gpsdata["idx"] = gpsdata.index
    gpsdata = gpsdata[(gpsdata.Gpstime > 0) & (gpsdata.idx == gpsdata.idx.shift() + 1)]
    del gpsdata["idx"]

    return gpsdata


def preprocess(canfile, gpsfile, outdir, zonesfile):

    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    candata = pandas.read_csv(canfile)
    gpsdata = pandas.read_csv(gpsfile)
    with open(zonesfile, "r") as f:
        zones = json.load(f)

    gpsdata = fix_gps(gpsdata)
    candata, gpsdata = make_gmt(candata, gpsdata)

    return candata, gpsdata, zones
