import json
from pathlib import Path
import folium
import folium.plugins
import tempfile
import os
import re


def plot_privpurge(message, outdir, filename=None):

    if filename is None:
        filename = "~map_" + next(tempfile._get_candidate_names()) + ".html"

    my_map = folium.Map()

    for dirpath, dirnames, filenames in os.walk(outdir):
        for fl in filenames:
            if re.search(r".{37}_GPS_Messages.csv", fl):
                with open(os.path.join(os.getcwd(), os.path.join(dirpath, fl))) as f:
                    f.readline()
                    points = [
                        tuple(map(float, l.split(",")[2:4][::-1]))
                        for l in f.readlines()
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


plot_privpurge("../~test_3/zonefile_2T3MWRFVXLW056972.json", "../~test_3/build")
