def gpx_lat_long_duration(name):
    import gpxpy
    import gpxpy.gpx
    with open(name) as gpx_one:
        gpx_one = gpxpy.parse(gpx_one)
        for track in gpx_one.tracks:
            longs = []
            times = []
            lats = []
            for segment in track.segments:
                for point in segment.points:
                    lats.append(point.latitude)
                    longs.append(point.longitude)
                    times.append(point.time)
            return lats, longs, times


def gpx_reader(name):
    import utm
    import datetime
    [lats, longs, times_dt] = gpx_lat_long_duration(name)
    east = []
    north = []
    times = []
    for i in (range(len(lats))):
        [eas, nor, _, _] = utm.from_latlon(lats[i], longs[i])
        east.append(eas)
        north.append(nor)
        time = (times_dt - datetime(1970,1,1)).total_seconds()
        times.append(time)
    

if __name__ == "__main__":
    gpx_reader('cycle_in_garmin.gpx')
