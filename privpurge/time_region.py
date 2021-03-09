import itertools


class time_region:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    @classmethod
    def create_many(cls, gpsdata, privregions):

        prev = gpsdata.Gpstime.iloc[0]
        mark = None

        intersects = [
            all(map(lambda reg: reg.intersects((lat, lon)), privregions))
            for lon, lat in zip(gpsdata.Long, gpsdata.Lat)
        ]
        result = [
            list(g)
            for k, g in itertools.groupby(
                zip(gpsdata.Gpstime.to_list(), intersects), key=lambda x: x[1]
            )
        ]
        result = [
            time_region(l[0][0], l[-1][0] if len(l) > 1 else l[0][0])
            for l in result
            if l[0][1]
        ]

        return result

    def intersects(self, time):
        pass

    def __repr__(self):
        return f"{(self.start, self.end)}"
