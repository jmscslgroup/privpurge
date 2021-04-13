from privpurge import run
from contextlib import redirect_stdout
from pathlib import Path
import io
import re
import os
import pytest

DATA_FOLDER = Path(__file__).parent.joinpath("data")

CAN = str(
    DATA_FOLDER.joinpath("{}/2020-09-15-15-43-34_5FNYF6H05HB089022_CAN_Messages.csv")
)
GPS = str(
    DATA_FOLDER.joinpath("{}/2020-09-15-15-43-34_5FNYF6H05HB089022_GPS_Messages.csv")
)
ZONE = str(DATA_FOLDER.joinpath("{}/zonefile_5FNYF6H05HB089022.json"))


@pytest.mark.parametrize("inp", ["pass_normal", "pass_empty", "pass_almost_empty"])
def test_pass(inp):
    run(
        CAN.format(inp),
        GPS.format(inp),
        f"{DATA_FOLDER.joinpath(inp)}/build",
        ZONE.format(inp),
        disable_output=True,
    )


@pytest.mark.parametrize(
    "inp",
    [
        "bad_gps_data",
        "mismatch_vin",
        "mismatch_time",
        "invalid_can",
        "invalid_gps",
        "invalid_zone",
    ],
)
def test_fail(inp):
    with pytest.raises(Exception):
        run(
            CAN.format(inp),
            GPS.format(inp),
            f"{DATA_FOLDER.joinpath(inp)}/build",
            ZONE.format(inp),
            disable_output=True,
        )


def test_check_output_names():
    f = io.StringIO()
    with redirect_stdout(f):
        test_pass("pass_normal")
    res = f.getvalue()

    out = re.search(r"Input:(.*)Output:(.*)", res, re.DOTALL)
    inputs = out.group(1).split()
    outputs = out.group(2).split()

    assert inputs[0] == os.path.abspath(
        str(
            DATA_FOLDER.joinpath(
                "pass_normal/2020-09-15-15-43-34_5FNYF6H05HB089022_CAN_Messages.csv"
            )
        )
    )
    assert inputs[1] == os.path.abspath(
        str(
            DATA_FOLDER.joinpath(
                "pass_normal/2020-09-15-15-43-34_5FNYF6H05HB089022_GPS_Messages.csv"
            )
        )
    )
    assert len(outputs) == 8
