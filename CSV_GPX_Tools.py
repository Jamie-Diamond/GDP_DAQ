import csv
import gpxpy
import gpxpy.gpx
from datetime import datetime
import utm
import matplotlib.pyplot as plt


def csv_2_gpx(input, output):
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    with open(input) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            long = row[None][3]
            lat = row[None][2]
            time = row[None][1]
            date = row[None][0]
            date_time_str = date + ' ' +time
            dt_object = datetime.strptime(date_time_str, '%d/%m/%Y %I:%M:%S.%f')
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, long, time=dt_object))

    file = open(output, "w")

    file.write(gpx.to_xml())

    file.close()



def gpx_spd_plot(name):
    with open(name) as gpx_one:
        gpx_one = gpxpy.parse(gpx_one)
        a=0
        for track in gpx_one.tracks:
            a+=1
            longs = []
            times = []
            lats = []
            for segment in track.segments:
                for point in segment.points:
                    lats.append(point.latitude)
                    longs.append(point.longitude)
                    times.append(point.time)

    distances = []
    speeds = []
    i = 0
    duration = [0]
    for i in (range(len(lats)-1)):
        [lat, long, _, _] = utm.from_latlon(lats[i], longs[i])
        [lat1, long1, _, _] = utm.from_latlon(lats[i+1], longs[i+1])
        latdiff = lat - lat1
        longdiff = long - long1
        time0 = times[i]
        time1 = times[i+1]
        timediff = time1 - time0
        duration.append(timediff.total_seconds() + duration[-1])
        dist = latdiff**2 + longdiff**2
        dist **= 0.5
        distances.append(dist)
        speed = dist/timediff.total_seconds()
        speeds.append(speed)

    del duration[0]

    print(len(speeds))
    print(len(duration))

    plt.plot(duration, speeds)
    plt.axis([0, max(duration), 0, 10])
    plt.show()

