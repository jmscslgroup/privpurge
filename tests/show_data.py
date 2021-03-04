import json
from pathlib import Path
import folium
import folium.plugins
import tempfile

from privpurge.privacy_region import privacy_region


def show_intersections(inputs, filename=None, save=None, no_compare=False):

    if filename is None:
        filename = "~map_" + next(tempfile._get_candidate_names()) + ".html"

    data = json.load(open(Path(__file__).parent.joinpath(f"data/{inputs}")))

    my_map = folium.Map()
    adder = folium.plugins.MarkerCluster().add_to(my_map)
    adder2 = folium.plugins.MarkerCluster().add_to(my_map)

    regions = privacy_region.create_many(data["MESSAGE"])

    for region in data["MESSAGE"]["regions"]:
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

    fres = []
    for (lon, lat), expected in data["INPUTS"]:

        results = [r.intersects((lat, lon)) for r in regions]
        if not no_compare:
            color = "red" if results != expected else "green"
            for i, (r, e) in enumerate(zip(results, expected)):
                if r != e:
                    print(
                        f"Found mismatch at {lon, lat} at intersection with {regions[i].type}"
                    )
        else:
            color = None

        if color != "red":
            c = sum(results)
            if c == 1:
                color = "green"
            elif c == 2:
                color = "blue"
            else:
                color = "purple"

        folium.Marker(
            location=[lat, lon],
            popup=f"{(lon, lat)}",
            icon=folium.Icon(color=color),
            fill_color=color,
        ).add_to(my_map)

        fres.append(results == expected)

    if save or (save is None and not all(fres)):
        my_map.save(filename)
        print(f"Map saved to: {filename}")

    return all(fres)
