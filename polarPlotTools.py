from sensor_log_ToolBox import sensor_log_read
from windDataTools import getWindData
from boatHeadingTools import addSpeedAndDirToGPS
from math import cos

Mag, Gyro, GPS, Accel, Lin_Accel = sensor_log_read('log.txt')

GPSWind = getWindData(GPS)
GPSWindHead = addSpeedAndDirToGPS(GPSWind, Mag)

def addApparentWind(GPSWindHead):
    for i in GPSWindHead:
        i[1]['App Wind Dir'] = i[1]['Heading'] - i[1]['Wind Dir']
        i[1]['App Wind Speed'] = i[1]['Wind Speed']*cos(i[1]['App Wind Dir'])

    return GPSWindHead
