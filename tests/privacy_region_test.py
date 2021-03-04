from pathlib import Path
import pytest
import json
import os

from privpurge.privacy_region import privacy_region
from .show_data import show_intersections

DATA_FOLDER = Path(__file__).parent.joinpath("data")
DEBUG = not os.environ.get("CI", False) and False


@pytest.mark.parametrize("inp", [f"intersect{i}.json" for i in range(1, (3) + 1)])
def test_region_intersection(inp):
    data = json.load(open(DATA_FOLDER.joinpath(inp)))
    message = data["MESSAGE"]
    inputs = data["INPUTS"]

    if DEBUG:
        res = show_intersections(inp, no_compare=True)
        assert res
    else:
        regions = privacy_region.create_many(message)

        for i in inputs:
            lon, lat = i[0]
            expected = i[1]
            for r, e in zip(regions, expected):
                res = r.intersects((lat, lon))
                assert (
                    res == e
                ), f"[{lat}, {lon}] {'not in' if res == False else 'in'} {r}"
