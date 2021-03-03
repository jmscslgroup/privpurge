import json
import shapely
import geopy.distance
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class privacy_region:
    def __init__(self, type, data):
        self.type = type
        self._data = data
        self.process_data(data)

    @classmethod
    def create_single(cls, regiondata):
        typ = regiondata["type"]
        dat = regiondata["data"]
        if typ not in ["circle", "polygon"]:
            raise TypeError(f"Invalid region type: {typ}")

        obj = privacy_circle if typ == "circle" else privacy_polygon
        return obj(typ, dat)

    @classmethod
    def create_many(cls, message):
        # vin = message["vin"]
        regions = message["regions"]

        return [privacy_region.create_single(a) for a in regions]

    def process_data(self, *args, **kwargs):
        raise NotImplementedError

    def intersects(self, coordinate):  # lat, lon
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class privacy_circle(privacy_region):
    def __init__(self, type, data):
        super().__init__(type, data)

    def process_data(self, data):
        self.center = tuple(reversed(data["center"]))  # size 2 tuple
        self.radius = data["radius"]

    def intersects(self, coordinate):  # latitude [-90, 90], longitude [-180, 180]
        return geopy.distance.distance(coordinate, self.center).m < self.radius

    def __str__(self):
        return f"[{self.type}] Center: {self.center}, Radius: {self.radius}"


class privacy_polygon(privacy_region):
    def __init__(self, type, data):
        super().__init__(type, data)

    def process_data(self, data):
        self.data = [tuple(reversed(a)) for a in data]  # list of coordinates

    def intersects(self, coordinate):  # latitude [-90, 90], longitude [-180, 180]
        return Polygon(self.data).intersects(Point(*coordinate))

    def __str__(self):
        return f"[{self.type}]: Coordinates: {self.data}"
