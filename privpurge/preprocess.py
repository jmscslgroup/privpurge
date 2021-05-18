import itertools
import json
import os
import pandas as pd

from datetime import datetime

from .utils import round_time


def trim_bad_ends(df):
    if any(sum(df.iloc[-1:].isnull().values.tolist(), start=[])):
        df = df[:-1]
    if any(sum(df.iloc[:1].isnull().values.tolist(), start=[])):
        df = df[1:]
    return df


def standardize_time(candata, gpsdata):

    c_one = datetime.fromtimestamp(candata.Time.iloc[0])
    g_one = datetime.fromtimestamp(gpsdata.Gpstime.iloc[0])  # gpstime in UTC

    diff = round_time(g_one, 60 * 60) - round_time(c_one, 60 * 60)

    candata.Time = [
        (datetime.fromtimestamp(c) + diff).timestamp() for c in candata.Time
    ]  # convert can time to gmt (gmt = utc+0)

    return candata, gpsdata


def negative_checking(list):

    s1 = sum(len(l) for l in list)
    last_negative_index = max(loc for loc, l in enumerate(list) if l[0] < 0)
    negative_at_end = last_negative_index == len(list) - 1

    if negative_at_end:
        raise ValueError(
            "Error found in gpsfile. Last grouped list has negative times."
        )

    pos_bw_neg_indices = [i for i in range(0, negative_at_end) if list[i][0] > 0]
    too_much_good_data = sum(len(list[i]) for i in pos_bw_neg_indices) > len(list[-1])

    if too_much_good_data:
        raise ValueError("Found too many good values before end of negatives.")

    list = [[False] * len(list[i]) for i in range(negative_at_end + 1)] + [
        [i > 0 for i in l] for l in list[negative_at_end + 1 :]
    ]
    list = sum(list, start=[])

    return list


def fix_gps(gpsdata):  # remove until consecutive negatives stop

    temp = [
        list(g)
        for k, g in itertools.groupby(gpsdata.Gpstime, lambda x: -1 if x < 0 else 1)
    ]
    temp = negative_checking(temp)

    gpsdata = gpsdata[temp]

    return gpsdata


def preprocess(canfile, gpsfile, outdir, zonesfile):

    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    candata = pd.read_csv(canfile)
    gpsdata = pd.read_csv(gpsfile)

    with open(zonesfile, "r") as f:
        zones = json.load(f)

    gpsdata = fix_gps(gpsdata)
    gpsdata = trim_bad_ends(gpsdata)
    candata = trim_bad_ends(candata)

    candata = candata.fillna(0)
    candata["Bus"] = candata["Bus"].astype(int)
    candata["MessageID"] = candata["MessageID"].astype(int)
    candata["MessageLength"] = candata["MessageLength"].astype(int)

    candata, gpsdata = standardize_time(candata, gpsdata)

    return candata, gpsdata, zones
