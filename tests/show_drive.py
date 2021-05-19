import json
import folium
import folium.plugins
import tempfile
import os
import re


def plot_privpurge(message, outdir, filename=None):

    if filename is None:
        filename = "~map_" + next(tempfile._get_candidate_names()) + ".html"

    my_map = folium.Map()

    for fl in [
        f for f in os.listdir(outdir) if os.path.isfile(os.path.join(outdir, f))
    ]:
        if re.search(r".{37}_GPS_Messages.csv", fl):
            with open(os.path.join(os.getcwd(), os.path.join(outdir, fl))) as f:
                f.readline()
                points = [
                    tuple(map(float, l.split(",")[2:4][::-1])) for l in f.readlines()
                ]
            folium.vector_layers.PolyLine(points).add_to(my_map)

    data = json.load(open(os.path.join(os.getcwd(), message)))

    for region in data["regions"]:
        if region["type"] == "circle":
            lon, lat = region["data"]["center"]
            rad = region["data"]["radius"]
            folium.vector_layers.Circle(
                location=[lat, lon], radius=rad, color="#3186cc", fill_color="#3186cc"
            ).add_to(my_map)
        elif region["type"] == "polygon":
            dat = [(lat, lon) for lon, lat in region["data"]]
            folium.vector_layers.Polygon(
                locations=dat, color="#3186cc", fill_color="#3186cc"
            ).add_to(my_map)

    my_map.save(filename)
    print(f"Map saved to: {filename}")


import argparse


def get_args():

    parser = argparse.ArgumentParser()

    parser.add_argument("directory")
    parser.add_argument("zonefile")
    parser.add_argument("-o", "--output")

    return parser.parse_args()


if __name__ == "__main__":
    cwd = os.getcwd()

    args = get_args()

    plot_privpurge(
        os.path.join(cwd, args.zonefile),
        os.path.join(cwd, args.directory),
        filename=args.output,
    )
