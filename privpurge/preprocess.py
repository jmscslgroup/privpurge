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


def create_negative_mask(grouped_list):

    list_ind_negative = [loc for loc, l in enumerate(grouped_list) if l[0] < 0]
    if not list_ind_negative:
        return True

    last_negative_index = list_ind_negative[-1]
    negative_at_end = last_negative_index == len(grouped_list) - 1

    if negative_at_end:
        raise ValueError(
            "Error found in gpsfile. Last grouped list has negative times."
        )

    pos_bw_neg_indices = [
        i for i in range(0, last_negative_index) if grouped_list[i][0] > 0
    ]
    too_much_good_data = sum(len(grouped_list[i]) for i in pos_bw_neg_indices) > len(
        grouped_list[-1]
    )

    if too_much_good_data:
        raise ValueError("Found too many good values before end of negatives.")

    masked_llist = [
        [False] * len(grouped_list[i])
        if i <= last_negative_index
        else [True] * len(grouped_list[i])
        for i in range(len(grouped_list))
    ]

    masked_list = sum(masked_llist, start=[])

    return masked_list


def fix_gps(gpsdata):  # remove until consecutive negatives stop

    temp = [
        list(g)
        for k, g in itertools.groupby(gpsdata.Gpstime, lambda x: -1 if x < 0 else 1)
    ]
    temp = create_negative_mask(temp)

    if temp is not True:
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
