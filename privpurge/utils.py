import regex
import os


def get_zonesfile(canfile):
    return "file"


def write_files(candata_t, gpsdata_t, outputdir):
    cfile, cdata = candata_t
    gfile, gdata = gpsdata_t

    cdata.to_csv(os.path.join(outputdir, os.path.basename(cfile)), index=False)
    gdata.to_csv(os.path.join(outputdir, os.path.basename(gfile)), index=False)


def write_error(err, filename, outputdir):
    name = os.path.splitext(os.path.basename(filename))[0]
    name.rstrip("CAN_Messages")
    name.rstrip("GPS_Messages")

    name += "ERROR.txt"
    filepath = os.path.join(outputdir, name)

    with open(filepath, "w") as f:
        f.write(err)

    print(f"Got an error. Saved to {filepath}.")
