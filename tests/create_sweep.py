import itertools
import pprint
import json


def frange(start, stop=None, step=None):
    # if set start=0.0 and step = 1.0 if not specified
    start = float(start)
    if stop == None:
        stop = start + 0.0
        start = 0.0
    if step == None:
        step = 1.0

    count = 0
    while True:
        temp = float(start + count * step)
        if step > 0 and temp >= stop:
            break
        elif step < 0 and temp <= stop:
            break
        yield temp
        count += 1


def create_sweep_data(xrange, yrange, xstep, ystep, n_regions):
    x = frange(*xrange, xstep)
    y = frange(*yrange, ystep)

    res = [list(a) for a in list(itertools.product(x, y))]
    return [list(a) for a in list(zip(res, [[True] * n_regions] * len(res)))]


def add_sweep_to_file(filename, xrange, yrange, xstep, ystep):
    with open(filename, "r") as f:
        dat = json.load(f)

    n_regions = len(dat["MESSAGE"]["regions"])

    dat["INPUTS"] = create_sweep_data(xrange, yrange, xstep, ystep, n_regions)

    with open(filename, "w") as f:
        json.dump(dat, f)


# add_sweep_to_file('data/intersect4.json', (-110.922, -110.904), (32.272, 32.283), 0.001, 0.001)
