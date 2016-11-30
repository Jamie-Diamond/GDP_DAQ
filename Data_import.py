def sensor_log_read(input='log.txt', t_offset=-4789.56):
    '''Reads data csv file form sensor_log and exports as lists'''
    import csv
    import json
    import time
    import sys
    t0 = time.time()
    with open(input) as csvfile:
        print('Opening: ' + input)
        next(csvfile)  # skip headings
        csvobj = csv.reader(csvfile, delimiter='\n')
        Magnetic = []
        Gyro = []
        GPS = []
        Accel = []
        Lin_Accel = []
        row_count = sum(1 for row in csv.reader(open(input), delimiter='\n'))
        levelCheck = 0.0
        i = 0
        for a in csvobj:
            if 'Magnetic' in a[0]:
                b = a[0].split("|")
                Magnetic.append([(float(b[3]) / 1000)+t_offset, json.loads(b[2])])
            if 'Gyro' in a[0]:
                b = a[0].split("|")
                Gyro.append([(float(b[3]) / 1000)+t_offset, json.loads(b[2])])
            if 'GPS' in a[0]:
                b = a[0].split("|")
                GPS.append([(float(b[3]) / 1000)+t_offset, json.loads(b[2])])
            if 'Acceleration' in a[0] and 'Linear' not in a[0]:
                b = a[0].split("|")
                Accel.append([(float(b[3]) / 1000)+t_offset, json.loads(b[2])])
            if 'Linear Acceleration' in a[0]:
                b = a[0].split("|")
                Lin_Accel.append([(float(b[3]) / 1000)+t_offset, json.loads(b[2])])
            i += 1
            if i > levelCheck:
                sys.stdout.write("\rProcessed Line: {:,.0f} of {:,.0f}. {:,.0f}%"
                                 "\t\tGPS: {:,.0f} | "
                                 "Mag: {:,.0f} | "
                                 "Gyro: {:,.0f} | "
                                 "Accelerometer: {:,.0f} | "
                                 "Linear-Acc: {:,.0f}"
                                 .format(i, row_count, (i/row_count)*100, len(GPS), len(Magnetic), len(Gyro), len(Accel), len(Lin_Accel)))
                sys.stdout.flush()
                levelCheck += 0.001 * row_count
    sys.stdout.write("\rProcessed Line: {:,.0f} of {:,.0f}. {:,.0f}%"
                     "\t\tGPS: {:,.0f} | "
                     "Mag: {:,.0f} | "
                     "Gyro: {:,.0f} | "
                     "Accelerometer: {:,.0f} | "
                     "Linear-Acc: {:,.0f}"
                     .format(i, row_count, (i / row_count) * 100, len(GPS), len(Magnetic), len(Gyro), len(Accel),
                             len(Lin_Accel)))
    sys.stdout.flush()
    print("\r\n")
    GPS = GPS_Data_Tidy(GPS)
    Magnetic = Mag_Data_Tidy(Magnetic)

    print("\r\nFinal Results:\r\n"
          "\r\nGPS: \t\t\t{:,.0f} @ {}Hz"
          "\r\nMagetic: \t\t{:,.0f} @ {}Hz"
          "\r\nGyroscope: \t\t{:,.0f} @ {}Hz"
          "\r\nAccelerometer: \t{:,.0f} @ {}Hz"
          "\r\nLinear-Acc: \t{:,.0f} @ {}Hz"
          .format(len(GPS), freq_out(GPS),
                  len(Magnetic), freq_out(Magnetic),
                  len(Gyro), freq_out(Gyro),
                  len(Accel), freq_out(Accel),
                  len(Lin_Accel), freq_out(Lin_Accel),
                  ))

    print('\r\n{:,.0f} lines read in: {:,.3f}s\r\n'.format(row_count, time.time() - t0))
    return Magnetic, Gyro, GPS, Accel, Lin_Accel


def data_import(file='saved', log='log.txt'):
    try:
        print('Trying to import processed Data')
        Magnetic, Gyro, GPS, Accel, Lin_Accel = data_read(file)
        print('imported Proccesed Data')
    except (FileNotFoundError, NameError):
        print('Importing of processed data FAILED, importing raw log')
        Magnetic, Gyro, GPS, Accel, Lin_Accel = sensor_log_read(log)
        print('Saving raw log file for future use')
        data_save(Magnetic, Gyro, GPS, Accel, Lin_Accel, file)
    print('Returning processed data')
    return Magnetic, Gyro, GPS, Accel, Lin_Accel


def freq_out(data):
    '''Returns recording frequency of data inputted'''
    from statistics import mean
    gap = []
    if len(data) < 501:
        return '-Not enough data points- '
    for i in range(500):
        t0 = (data[i][0])
        t1 = (data[i + 1][0])
        gap.append(t1 - t0)
    ave = mean(gap)
    freq = 1 / ave
    return str(round(freq, 1))


def GPS_Data_Tidy(GPS):
    '''Procceses GPS data into correct format'''
    print('Proccesing GPS data')
    import utm
    new_GPS = []
    idx = -1
    for i in GPS:
        t = i[1]['mTime'] / 1000
        ac = i[1]['mAccuracy']
        lon = i[1]['mLongitude']
        lat = i[1]['mLatitude']
        [Easting, Northing, _, _] = utm.from_latlon(lat, lon)
        try:
            if t != new_GPS[idx][0]:
                new_GPS.append([t, {'Accuracy': ac, 'Easting': Easting, 'Northing': Northing}])
                idx += 1
        except IndexError:
            new_GPS.append([t, {'Accuracy': ac, 'Easting': Easting, 'Northing': Northing}])
            idx += 1
    return new_GPS


def Mag_Data_Tidy(Mag):
    '''Procceses mag data into correct format'''
    print('Proccesing mag data')
    import math
    new_mag = []
    for i in Mag:
        time = i[0]
        ang = math.atan2(i[1][1], i[1][0])
        ang *= 180 / (math.pi)
        ang = Wrapto0_360(ang)
        new_mag.append([time, ang])
    return new_mag


def getDayWindData(GPS, loc):
    import urllib.request
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
    import datetime
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
                    "GWS": j[2],
                    "GWD": j[3],
                    "GWG": j[4]
                }])
                found = True
                break
        if not found:
            print(time + " for " + str(i) + " not found. ")

    return alignedData


def getPointRelPos(dataPoint, coordLoc1, coordLoc2):
    import utm
    import numpy
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
    import numpy
    import sys
    sotonLatLong = [50.883500, -1.394333]
    brambleLatLong = [50.790167, -1.285833]
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
                GPS[int(i)][1]['GWS'] = interpolatedDataPoint[1]['GWS']
                GPS[int(i)][1]['GWD'] = interpolatedDataPoint[1]['GWD']
                GPS[int(i)][1]['GWG'] = interpolatedDataPoint[1]['GWG']
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


def addSpeedAndDirToGPS(GPS, Mag):
    from math import atan2
    from math import sqrt
    import sys
    index = 0
    utmOld = None
    utmNew = None
    for i in GPS:
        if index == 0:
            i[1]["SOG"] = 0
            i[1]["HDG"] = 0
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

            #Direction = (GPSDirection + MagDirection) / 2
            #COW = COG-TIDE

            Leeway = abs(GPSDirection - MagDirection)

            if Leeway > 180:
                Leeway = 360 - Leeway

            GPS[index][1]["COG"] = GPSDirection
            GPS[index][1]["SOG"] = Speed
            GPS[index][1]["HDG"] = MagDirection
            GPS[index][1]["LWY"] = Leeway

            utmOld = [i[1]["Easting"], i[1]["Northing"]]
            tOld = i[0]

        sys.stdout.write("\rBoat Heading and Direction: Processed GPS Point: {:,.0f} of {:,.0f}."
                         .format(index+1, len(GPS)))
        sys.stdout.flush()

        index += 1

    print('\r\nComplete.\r\n')

    return GPS


def Wrapto0_360(x):
    if x < 0:
        x += 360
    return x

def Wrapto180(x):
    x = Wrapto0_360(x)
    if x > 180:
        x = 360 - x
    return x

def addApparentWind(GPSWindHead):
    import sys
    index = 0
    for i in GPSWindHead:
        if index == 0:
            i[1]['AWA'] = None
            i[1]['AWS'] = None
            i[1]['TWA'] = None
        else:
            try:
                i[1]['TWA'] = Wrapto180(i[1]['HDG'] - i[1]['GWD'])
                i[1]['AWA'] = None ####################### Add Equation here ########################
                i[1]['AWS'] = None#i[1]['Wind Speed']*cos(i[1]['App Wind Dir'])
            except KeyError:
                print('Something not found in: ' + str(i))

        sys.stdout.write("\rApparent Wind Speed and Direction: Processed GPS Point: {:,.0f} of {:,.0f}. "
                         .format(index + 1, len(GPSWindHead)))
        sys.stdout.flush()

        index += 1

    print('\r\nComplete.\r\n')
    return GPSWindHead


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
    import warnings
    warnings.warn('No match found in bisect method')
    return dataList[correctedIndex], iterations


def data_save(data, file='Data_Save'):
    import json
    print('Saving Dictionary to File')
    file += '.json'
    with open(file, 'w') as out_file:
        js = json.dumps(data)
        out_file.write(js)
    return None


def data_read(file = 'Data_Save'):
    import json
    file += '.json'
    with open(file) as txt:
        dat = json.load(txt)
    return dat


def PP_data_import(reprocess=False, file='Data_Save', input='log.txt'):
    try:
        if reprocess:
            print('Reprocess Requested')
            raise FileNotFoundError
        else:
            data = data_read(file)
            return data
    except (NameError, FileNotFoundError):
        print('No Processed Saved Data Found \n Starting from log.txt \n \n')
        Mag, Gyro, GPS, Accel, Lin_Accel = sensor_log_read(input)
        data = getWindData(GPS)
        data = addSpeedAndDirToGPS(data, Mag)
        data = addApparentWind(data)
        data_save(data)
        print('-++'*30, '\nSaving Processed Data For Future use as', file, '.JSON \n', '-++'*30)
        return data


if __name__ == "__main__":
  data = PP_data_import()
  from Plotting_ToolBox import Mag_plot
  Mag_plot(data)



