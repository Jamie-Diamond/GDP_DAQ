from math import sqrt
from math import atan

import sys


def addSpeedAndDirToGPS(GPS, Mag):
    index = 0
    utmOld = None
    utmNew = None
    for i in GPS:
        if index == 0:
            i[1]["Speed"] = None
            i[1]["Direction"] = None
            utmOld = [i[1]["Easting"], i[1]["Northing"]]
            tOld = i[0]
        else:
            utmNew = [i[1]["Easting"], i[1]["Northing"]]
            tNew = i[0]

            dt = tNew - tOld
            ds = sqrt((utmNew[0] - utmOld[0]) ** 2 + (utmNew[1] - utmOld[1]) ** 2)
            Speed = (ds / dt) / 0.5144

            try:
                GPSDirection = atan((utmNew[0] - utmOld[0]) / (utmNew[1] - utmOld[1]))
            except ZeroDivisionError:
                GPSDirection = 90

            nearestTimeStamp = None

            for j in Mag:
                if nearestTimeStamp == None:
                    nearestTimeStamp = j
                elif abs(i[0] - j[0]) < abs(i[0] - nearestTimeStamp[0]):
                    nearestTimeStamp = j

            MagDirection = nearestTimeStamp[1]

            Direction = (GPSDirection + MagDirection) / 2

            Leeway = abs(GPSDirection - MagDirection)

            if Leeway > 180:
                Leeway = 360 - Leeway

            GPS[index][1]["Speed"] = Speed
            GPS[index][1]["Direction"] = Direction
            GPS[index][1]["Leeway"] = Leeway

            utmOld = [i[1]["Easting"], i[1]["Northing"]]
            tOld = i[0]

        sys.stdout.write("\rBoat Heading and Direction: Processed GPS Point: {:,.0f} of {:,.0f}."
                         .format(index+1, len(GPS)))
        sys.stdout.flush()

        index += 1

    print('\r\nComplete.\r\n')

    return GPS