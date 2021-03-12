import argparse
import os
import traceback
import sys

from .preprocess import preprocess
from .utils import (
    get_zonesfile,
    write_files,
    write_error,
    check_parse_files,
    gmt_error_date,
)
from .privacy_region import privacy_region
from .time_region import time_region
from .process import remove


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Purging privacy regions from collected data.",
        add_help=False,
        prog="privpurge",
    )

    required = parser.add_argument_group("Required Arguments")
    optional = parser.add_argument_group("Optional Arguments")

    required.add_argument("can", help="csv file for can data")
    required.add_argument("gps", help="csv file for gps data")
    required.add_argument(
        "-o", "--output", help="specify output directory", required=True
    )

    optional.add_argument(
        "-z", "--zones", help="specify file for privacy zones", required=False
    )
    optional.add_argument(
        "-h", "--help", action="help", help="Show this help message and exit"
    )

    if len(sys.argv) == 1:
        parser.print_usage()
        sys.exit(1)

    return parser.parse_args()


def main():
    args = get_arguments()
    canfile = args.can
    gpsfile = args.gps
    outdir = os.path.join(os.getcwd(), args.output)
    zonesfile = args.zones if args.zones else get_zonesfile(canfile)

    orig_time, vin = check_parse_files(canfile, gpsfile, zonesfile)
    error_date = gmt_error_date(canfile, gpsfile)

    try:

        candata, gpsdata, zones = preprocess(canfile, gpsfile, outdir, zonesfile)

        privregions = privacy_region.create_many(zones)
        timeregions = time_region.create_many(gpsdata, privregions)

        filepairs = remove(candata, gpsdata, timeregions)

        write_files(filepairs, vin, outdir)

    except Exception as e:
        write_error(error_date, vin, traceback.format_exc(), outdir)


if __name__ == "__main__":
    main()
