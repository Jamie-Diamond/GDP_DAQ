from math import sqrt
from math import atan2

import sys


def bisect(target, dataList):
    length = len(dataList)
    correctedIndex = int(length / 2)
    correctionFactor = int(length / 2)

    iterations = 0

    while correctionFactor > 1:

        iterations += 1
        correctionFactor = int(correctionFactor / 2)

        if dataList[correctedIndex][0] > target:
            correctedIndex -= correctionFactor
        elif dataList[correctedIndex][0] < target:
            correctedIndex += correctionFactor
        elif dataList[correctedIndex][0] == target:
            return dataList[correctedIndex], iterations

    return dataList[correctedIndex], iterations

def addSpeedAndDirToGPS(GPS, Mag):
    index = 0
    utmOld = None
    utmNew = None
    for i in GPS:
        if index == 0:
            i[1]["Speed"] = 0
            i[1]["Heading"] = 0
            utmOld = [i[1]["Easting"], i[1]["Northing"]]
            tOld = i[0]
        else:
            utmNew = [i[1]["Easting"], i[1]["Northing"]]
            tNew = i[0]

            dt = tNew - tOld
            ds = sqrt((utmNew[0] - utmOld[0]) ** 2 + (utmNew[1] - utmOld[1]) ** 2)
            Speed = (ds / dt) / 0.5144

            GPSDirection = atan2((utmNew[0] - utmOld[0]) , (utmNew[1] - utmOld[1]))


            nearestTimeStamp, iterations = bisect(i[0], Mag)
            MagDirection = nearestTimeStamp[1]

            Direction = (GPSDirection + MagDirection) / 2

            Leeway = abs(GPSDirection - MagDirection)

            if Leeway > 180:
                Leeway = 360 - Leeway

            GPS[index][1]["Speed"] = Speed
            GPS[index][1]["Heading"] = Direction
            GPS[index][1]["Leeway"] = Leeway

            utmOld = [i[1]["Easting"], i[1]["Northing"]]
            tOld = i[0]

        sys.stdout.write("\rBoat Heading and Direction: Processed GPS Point: {:,.0f} of {:,.0f}."
                         .format(index+1, len(GPS)))
        sys.stdout.flush()

        index += 1

    print('\r\nComplete.\r\n')

    return GPS