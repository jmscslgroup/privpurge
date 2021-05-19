from functools import reduce


def remove_split(df, timeregions, key):

    df.reset_index(drop=True, inplace=True)

    if not timeregions:
        return [df]

    intersections = [time @ df[key] for time in timeregions]
    public_bool = (~reduce(lambda x, y: x | y, intersections)).to_list()

    if all(public_bool):
        return [df]

    switch_idx = [
        i for i, (x, y) in enumerate(zip(public_bool[:-1], public_bool[1:])) if x != y
    ]

    res = []
    last_check = 0
    for i in switch_idx:
        res.append(df.iloc[last_check : i + 1])
        last_check = i + 1
    res.append(df.iloc[last_check:])

    cur_len = 0
    new_res = []
    for subframe in res:
        if public_bool[cur_len]:
            new_res.append(subframe)
        cur_len += len(subframe)

    return new_res


def get_intervals(df_list, key):
    intervals = []
    for df in df_list:
        intervals.append((df[key].iloc[0], df[key].iloc[-1]))
    return intervals


def find_intersections(can_intervals, gps_intervals):

    intersectsions = []

    for cidx, cin in enumerate(can_intervals):
        for gidx, gin in enumerate(gps_intervals):
            cleft, cright = cin
            gleft, gright = gin

            ileft, iright = max(cleft, gleft), min(cright, gright)
            if ileft > iright:
                continue

            intersectsions.append((cidx, gidx))

    return intersectsions


def smartzip(candatas, gpsdatas):

    can_intervals = get_intervals(candatas, "Time")
    gps_intervals = get_intervals(gpsdatas, "Gpstime")

    intersections = find_intersections(can_intervals, gps_intervals)

    # sorted by can_indices
    sorted_intersections = sorted(intersections, key=lambda pair: pair[0])

    # check gps_indices are strictly increasing
    gps_indices = [g for _, g in intersections]
    assert all(l < r for l, r in zip(gps_indices, gps_indices[1:]))

    zipped = [(candatas[c], gpsdatas[g]) for c, g in sorted_intersections]

    return zipped


def remove(candata, gpsdata, timeregions):

    candatas = remove_split(candata, timeregions, "Time")
    gpsdatas = remove_split(gpsdata, timeregions, "Gpstime")

    return (
        zip(candatas, gpsdatas)
        if len(candatas) == len(gpsdatas)
        else smartzip(candatas, gpsdatas)
    )
