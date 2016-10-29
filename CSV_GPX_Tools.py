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


def gpx_spd(name):
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
    plt.figure(1)
    plt.plot(longs,lats)
    plt.show
    distances = []
    speeds = []
    i = 0
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
    print(numpy.mean(timediff_lst))

    print(len(speeds))
    print(len(duration))
    if 'garmin' in name:
        x = 1
    else:
        x = 6
    speeds_ave = movingaverage(speeds, x)

    return speeds_ave, duration

if __name__ == "__main__":
    [gs, gd] = gpx_spd('cycle_in_garmin.gpx')
    [ps, pd] = gpx_spd('cycle_in.gpx')

    plt.figure(2)
    pd[:] = [x - 5 for x in pd]
    line_up, = plt.plot(gd,gs, 'rx-', label='Garmin')
    line_down, = plt.plot(pd, ps, 'bx-', label='Android App')
    plt.legend(handles=[line_up, line_down])
    plt.ylim(0, 14)
    plt.xlim(0, 350)
    plt.xlabel("Duration [s]")
    plt.ylabel("Speed [m/s]")
    plt.grid(True)
    plt.show()

