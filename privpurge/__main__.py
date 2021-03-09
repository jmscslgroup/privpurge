import argparse
import os
import traceback

from .preprocess import preprocess
from .utils import get_zonesfile, write_files, write_error
from .privacy_region import privacy_region
from .time_region import time_region


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

    return parser.parse_args()


def main():
    args = get_arguments()
    canfile = args.can
    gpsfile = args.gps
    outdir = os.path.join(os.getcwd(), args.output)
    zonesfile = args.zones if args.zones else get_zonesfile(canfile)

    try:
        candata, gpsdata, zones = preprocess(canfile, gpsfile, outdir, zonesfile)

        privregions = privacy_region.create_many(zones)
        timeregions = time_region.create_many(gpsdata, privregions)

        # remove from files

        write_files((canfile, candata), (gpsfile, gpsdata), outdir)

    except Exception as e:
        write_error(traceback.format_exc(), canfile, outdir)


if __name__ == "__main__":
    main()
