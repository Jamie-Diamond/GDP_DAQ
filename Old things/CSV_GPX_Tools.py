import csv
import gpxpy
import gpxpy.gpx
from datetime import datetime
import utm
import matplotlib.pyplot as plt
#from pykalman import KalmanFilter
import numpy

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

def movingaverage(interval, window_size):
    window= numpy.ones(int(window_size))/float(window_size)
    return numpy.convolve(interval, window, 'same')


def gpx_lat_long_duration(name):
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


def gpx_spd(lats, longs, times):
    distances = []
    speeds = []
    duration = [0]
    timediff_lst = []
    for i in (range(len(lats)-1)):
        [lat, long, _, _] = utm.from_latlon(lats[i], longs[i])
        [lat1, long1, _, _] = utm.from_latlon(lats[i+1], longs[i+1])
        latdiff = lat - lat1
        longdiff = long - long1
        time0 = times[i]
        time1 = times[i+1]
        timediff = time1 - time0
        timediff_lst.append(timediff)
        duration.append(timediff.total_seconds() + duration[-1])
        dist = latdiff**2 + longdiff**2
        dist **= 0.5
        distances.append(dist)
        speed = dist/timediff.total_seconds()
        speeds.append(speed)

    del duration[0]
    return speeds, duration

if __name__ == "__main__":
    from Karman_filter import lat_long_karman
    [latsgar, longsgar, timesgar] = gpx_lat_long_duration('cycle_in_garmin.gpx')
    [lats, longs, times] = gpx_lat_long_duration('cycle_in.gpx')
    [latsK, longsK] = lat_long_karman(lats, longs)
    plt.figure(1)
    plt.plot(longsgar, latsgar, 'g*-', label='Garmin')
    plt.plot(longs, lats, 'bo-', label='Phone Raw')
    plt.plot(longsK, latsK, 'rx-', label='Phone Karman Filtered')
    plt.legend()

    [latsgar, longsgar, timesgar] = gpx_lat_long_duration('cycle_in_garmin.gpx')
    [lats, longs, times] = gpx_lat_long_duration('cycle_in.gpx')
    [latsK, longsK] = lat_long_karman(lats, longs)
    [gs, gd] = gpx_spd(latsgar, longsgar, timesgar)
    [ps, pd] = gpx_spd(lats, longs, times)
    [psK, pdK] = gpx_spd(latsK, longsK, times)

    plt.figure(2)
    offset = 5
    pd[:] = [x - offset for x in pd]
    plt.plot(gd, gs, 'rx-', label='Garmin')
    plt.plot(pd, ps, 'bx-', label='Android App')
    plt.plot(pdK, psK, 'k*-', label='Android App Karman')
    plt.legend()
    plt.ylim(0, 14)
    plt.xlim(0, 350)
    plt.xlabel("Duration [s]")
    plt.ylabel("Speed [m/s]")
    plt.grid(True)
    plt.show()

