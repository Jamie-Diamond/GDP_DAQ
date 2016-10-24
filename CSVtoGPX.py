import csv
import gpxpy
import gpxpy.gpx
from datetime import datetime

gpx = gpxpy.gpx.GPX()
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)

# Create first segment in our GPX track:
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

with open('data2') as csvfile:
    reader = csv.DictReader(csvfile)
    #a = 0
    for row in reader:
        long = row[None][3]
        lat = row[None][2]
        time = row[None][1]
        date = row[None][0]
        date_time_str = date + ' ' +time
        date_time_str, decimal_secs = date_time_str.split('.')
        dt_object = datetime.strptime(date_time_str, '%d/%m/%Y %I:%M:%S')
        time_object = dt_object.replace(microsecond=int(decimal_secs))
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, long, time=dt_object))
        #a += 1



print ('Created GPX:', gpx.to_xml() )

file = open("gpxtest2.gpx", "w")

file.write(gpx.to_xml())

file.close()

