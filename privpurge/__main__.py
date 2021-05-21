import argparse
import sys

from .preprocess import preprocess
from .privacy_region import privacy_region
from .process import remove
from .time_region import time_region
from .utils import (
    check_parse_files,
    csv_is_empty,
    write_files,
)


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
    required.add_argument(
        "-z", "--zones", help="specify file for privacy zones", required=True
    )

    optional.add_argument(
        "-h", "--help", action="help", help="Show this help message and exit"
    )

    if len(sys.argv) == 1:
        parser.print_usage()
        sys.exit(1)

    return parser.parse_args()


def run(canfile, gpsfile, outdir, zonesfile, disable_output=False):

    orig_time, vin = check_parse_files(canfile, gpsfile, zonesfile)
    if any(map(csv_is_empty, (canfile, gpsfile))):
        write_files(
            [],
            vin,
            canfile,
            gpsfile,
            outdir,
            write=not disable_output,
        )
        return

    candata, gpsdata, zonejson = preprocess(canfile, gpsfile, zonesfile)

    privregions = privacy_region.create_many(zonejson)
    timeregions = time_region.create_many(gpsdata, privregions)

    filepairs = remove(candata, gpsdata, timeregions)

    write_files(filepairs, vin, canfile, gpsfile, outdir, write=not disable_output)


def main():
    args = get_arguments()
    run(args.can, args.gps, args.output, args.zones)


if __name__ == "__main__":
    main()
