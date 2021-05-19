import itertools
import json
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

    negative_at_end = grouped_list[-1][0] < 0

    if negative_at_end:
        raise ValueError(
            "Error found in gpsfile. Last grouped list has negative times."
        )

    total_size = sum(len(sublist) for sublist in grouped_list)
    good_size = len(grouped_list[-1])
    bad_size = total_size - good_size

    masked_list = [False] * bad_size + [True] * good_size

    return masked_list


def fix_gps(gpsdata):  # remove until consecutive negatives stop

    grouped_by_negatives = [
        list(g)
        for k, g in itertools.groupby(gpsdata.Gpstime, lambda x: -1 if x < 0 else 1)
    ]
    mask = create_negative_mask(grouped_by_negatives)

    if mask is not True:
        gpsdata = gpsdata[mask]

    return gpsdata


def preprocess(canfile, gpsfile, zonesfile):

    candata = pd.read_csv(canfile)
    gpsdata = pd.read_csv(gpsfile)

    with open(zonesfile, "r") as f:
        zonejson = json.load(f)

    gpsdata = fix_gps(gpsdata)
    gpsdata = trim_bad_ends(gpsdata)
    candata = trim_bad_ends(candata)

    candata = candata.fillna(0)
    candata["Bus"] = candata["Bus"].astype(int)
    candata["MessageID"] = candata["MessageID"].astype(int)
    candata["MessageLength"] = candata["MessageLength"].astype(int)

    candata, gpsdata = standardize_time(candata, gpsdata)

    return candata, gpsdata, zonejson
