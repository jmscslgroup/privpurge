from functools import reduce


def remove_split(df, timeregions, key):

    df.reset_index(drop=True, inplace=True)

    private_bool = reduce(lambda x, y: x | y, [time @ df[key] for time in timeregions])

    if all(
        ~private_bool
    ):  # if there is nothing to remove, so inverse of mask is all True
        return [df]

    private_regions = df[private_bool]
    orig_idx = set(df.index)
    private_idx = set(private_regions.index)

    public_idx = sorted(list(orig_idx ^ private_idx))
    public_lst = [[public_idx[0]]]
    for cur, next in zip(public_idx, public_idx[1:]):
        if cur + 1 != next:
            public_lst.append([next])
        else:
            public_lst[-1].append(next)

    public_lst = [l if len(l) > 1 else [l[0], l[0]] for l in public_lst]

    res = []
    for section in public_lst:
        res.append(df.iloc[section[0] : section[-1] + 1])

    return res


def remove(candata, gpsdata, timeregions):

    candatas = remove_split(candata, timeregions, "Time")
    gpsdatas = remove_split(gpsdata, timeregions, "Gpstime")

    if len(candatas) != len(gpsdatas):
        print(len(candatas), len(gpsdatas))
        raise ValueError(
            "Mismatching data in CAN and GPS files. A portion was removed from one but not the other."
        )

    return zip(candatas, gpsdatas)
