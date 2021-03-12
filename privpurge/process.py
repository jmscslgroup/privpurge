def remove_split(df, timeregions, key):

    df.reset_index(drop=True, inplace=True)

    rem = [[df.index[0] - 1]]
    keep = []

    for time in timeregions:
        to_remove = time @ df[key]
        rem.append(to_remove)

    rem.append([df.index[-1] + 1])

    if [] in rem:
        rem.remove([])

    for previous, current in zip(rem, rem[1:]):
        if current and previous:
            keep.append(list(range(previous[-1] + 1, current[0])))

    if [] in keep:
        keep.remove([])

    res = []
    for l in keep:
        res.append(df.iloc[l[0] : l[-1] + 1])

    return res


def remove(candata, gpsdata, timeregions):

    candatas = remove_split(candata, timeregions, "Time")
    gpsdatas = remove_split(gpsdata, timeregions, "Gpstime")

    if len(candatas) != len(gpsdatas):
        raise ValueError(
            "Mismatching data in CAN and GPS files. A portion was removed from one but not the other."
        )

    return zip(candatas, gpsdatas)
