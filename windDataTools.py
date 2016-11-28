import urllib.request
import datetime
import sys
import matplotlib.pyplot
import numpy
import utm

sotonLatLong = [50.883500, -1.394333]
brambleLatLong = [50.790167, -1.285833]

def getDayWindData(GPS, loc):
    listData = [[]]
    firstTimeStamp = GPS[0][0]
    url = createurl(loc, firstTimeStamp)
    if url != False:
        print("Data retrieved from: " + url)
        response = urllib.request.urlopen(url).read().decode('utf-8').replace('"', '').split(",")
        for i in response:
            if "\r\n" in i:
                splitData = i.split("\r\n")
                listData[-1].append(splitData[0])
                if len(splitData[1]) > 0:
                    listData.append([splitData[1]])
            else:
                listData[-1].append(i)
        return listData
    else:
        print("Error creating url.")
        return False


def createurl(website, timeStamp):
    rmin, min, hour, day, sMonth, lMonth, year = convertTimeStamp(timeStamp)
    if website == "Soton":
        url = "http://www.sotonmet.co.uk/archive/" + year + "/" + lMonth + "/CSV/Sot" + day + sMonth + year + ".csv"
    elif website == "Bramble":
        url = "http://www.bramblemet.co.uk/archive/" + year + "/" + lMonth + "/CSV/Bra" + day + sMonth + year + ".csv"
    elif website == "Cowes":
        url = False
    else:
        url = False

    return url


def convertTimeStamp(timeStamp):
    fromStamp = datetime.datetime.fromtimestamp(timeStamp)
    if roundNo(fromStamp.strftime('%M')) == 60:
        rmin = '00'
        hour = str(int(fromStamp.strftime('%H')) + 1)
    else:
        rmin = str(roundNo(fromStamp.strftime('%M')))
        hour = fromStamp.strftime('%H')
    return rmin, \
           fromStamp.strftime('%M'), \
           hour, \
           fromStamp.strftime('%d'), \
           fromStamp.strftime('%b'), \
           fromStamp.strftime('%B'), \
           fromStamp.strftime('%Y')


def roundNo(x, base=5):
    return int(base * round(float(x) / base))


def alignGPSTimeAndWindData(GPS, rawWind):
    alignedData = []
    for i in GPS:
        found = False
        timeStamp = i[0]
        rmin, min, hour, day, sMonth, lMonth, year = convertTimeStamp(timeStamp)
        time = "%02d:%02d" % (int(hour), int(rmin))
        #print(time)
        for j in rawWind:
            if j[1] == time:
                alignedData.append([timeStamp, {
                    "Wind Speed": j[2],
                    "Wind Dir": j[3],
                    "Wind Gust": j[4]
                }])
                found = True
                break
        if not found:
            print(time + " for " + str(i) + " not found. ")

    return alignedData

def getPointRelPos(dataPoint, coordLoc1, coordLoc2):
    utmLoc1 = utm.from_latlon(coordLoc1[0], coordLoc1[1])
    utmLoc2 = utm.from_latlon(coordLoc2[0], coordLoc2[1])
    pointX = dataPoint[1]["Easting"]
    pointY = dataPoint[1]["Northing"]

    refdx = (utmLoc1[0] - utmLoc2[0])
    refdy = (utmLoc1[1] - utmLoc2[1])
    m = refdy/refdx
    refC = utmLoc1[1] - (m * utmLoc1[0])
    datC = pointY - (m * pointX)
    dC = datC - refC
    lineSeperation = dC * numpy.cos(numpy.arctan(m))
    linedx = -lineSeperation * numpy.sin(numpy.arctan(m))
    linedy = lineSeperation * numpy.cos(numpy.arctan(m))


    utmLoc1Mapped = [utmLoc1[0] + linedx, utmLoc1[1] + linedy]
    utmLoc2Mapped = [utmLoc2[0] + linedx, utmLoc2[1] + linedy]

    # matplotlib.pyplot.plot(utmLoc1[0], utmLoc1[1], 'ro')
    # matplotlib.pyplot.plot(utmLoc2[0], utmLoc2[1], 'go')
    # matplotlib.pyplot.plot(pointX, pointY, 'b+')
    #
    # matplotlib.pyplot.plot(numpy.linspace(utmLoc1[0], utmLoc2[0], num=100), numpy.linspace(utmLoc1[0], utmLoc2[0], num=100) * m + refC, 'r')
    # matplotlib.pyplot.plot(numpy.linspace(utmLoc1[0], utmLoc2[0], num=100), numpy.linspace(utmLoc1[0], utmLoc2[0], num=100) * m + datC, 'b')
    # matplotlib.pyplot.plot([utmLoc2[0], utmLoc2[0]], [utmLoc2[1], utmLoc2[1]+dC], 'g')
    # matplotlib.pyplot.plot([utmLoc1[0], utmLoc1[0] + linedx], [utmLoc1[1], utmLoc1[1]], 'g')
    # matplotlib.pyplot.plot([utmLoc1[0] + linedx, utmLoc1[0] + linedx], [utmLoc1[1], utmLoc1[1] + linedy], 'g')
    # matplotlib.pyplot.plot(utmLoc1Mapped[0], utmLoc1Mapped[1], 'r+')
    # matplotlib.pyplot.plot(utmLoc2Mapped[0], utmLoc2Mapped[1], 'g+')
    # matplotlib.pyplot.show()

    percX = (pointX - utmLoc2Mapped[0])/(utmLoc1Mapped[0] - utmLoc2Mapped[0])
    percY = (pointY - utmLoc2Mapped[1]) / (utmLoc1Mapped[1] - utmLoc2Mapped[1])

    return percX, percY

def interpolateData(dataPoint1, dataPoint2, percAlongConnectingLine):
    interpolatedDataPoint = [dataPoint1[0], {}]
    for i in dataPoint1[1]:
        interpolatedDataPoint[1][i] = (float(dataPoint1[1][i]) - float(dataPoint2[1][i])) * percAlongConnectingLine + float(dataPoint2[1][i])
    return interpolatedDataPoint

def getWindData(GPS):
    sotonWindData = getDayWindData(GPS, "Soton")
    brambleWindData = getDayWindData(GPS, "Bramble")

    sotonAlignedData = alignGPSTimeAndWindData(GPS, sotonWindData)
    brambleAlignedData = alignGPSTimeAndWindData(GPS, brambleWindData)

    interpolatedDataPoint = []

    count = 1
    print("")

    for i in numpy.linspace(0, len(GPS)-1, num=(len(GPS))):
        percX, percY = getPointRelPos(GPS[int(i)], sotonLatLong, brambleLatLong)
        percDiff = numpy.abs(100 * (percY - percX))
        percAve = (percX + percY) / 2
        if (percDiff < 1e-6):
            try:
                interpolatedDataPoint = interpolateData(sotonAlignedData[int(i)], brambleAlignedData[int(i)], percAve)
                GPS[int(i)][1]['Wind Speed'] = interpolatedDataPoint[1]['Wind Speed']
                GPS[int(i)][1]['Wind Dir'] = interpolatedDataPoint[1]['Wind Dir']
                GPS[int(i)][1]['Wind Gust'] = interpolatedDataPoint[1]['Wind Gust']
            except IndexError:
                print("Index " + str(i) + " not found in [soton: " + str(len(sotonAlignedData)) + "] or [bramble: " + str(len(sotonAlignedData)) + "]")

            sys.stdout.write("\rGetting Wind Data: Processed GPS Point: {:,.0f} of {:,.0f}. "
                             .format(count, len(GPS)))
            sys.stdout.flush()
        else:
            print("Error interpolating between reference points.")
            return False
        count += 1

    print('\r\nComplete.\r\n')

    # print("Soton data:")
    # for data in sotonAlignedData[:10]:
    #     print(data)
    # print("Bramble data: ")
    # for data in brambleAlignedData[:10]:
    #     print(data)
    # print("Interpolated data: ")
    # for data in interpolatedData[:10]:
    #     print(data)

    return GPS