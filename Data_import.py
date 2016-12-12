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

    percX = (pointX - utmLoc2Mapped[0])/(utmLoc1Mapped[0] - utmLoc2Mapped[0])
    percY = (pointY - utmLoc2Mapped[1]) / (utmLoc1Mapped[1] - utmLoc2Mapped[1])

    return percX, percY


def interpolateData(dataPoint1, dataPoint2, percAlongConnectingLine):
    interpolatedDataPoint = [dataPoint1[0], {}]
    #for i in dataPoint1[1]:
        #interpolatedDataPoint[1][i] = (float(dataPoint1[1][i]) - float(dataPoint2[1][i])) * percAlongConnectingLine + float(dataPoint2[1][i])
    
    #print(dataPoint1)
    
    X1, Y1 = to_vector(dataPoint1[1]["GWD"], dataPoint1[1]["GWS"])
    X2, Y2 = to_vector(dataPoint1[1]["GWD"], dataPoint1[1]["GWS"])

    X3 = (X1 - X2) * percAlongConnectingLine + X1
    Y3 = (Y1 - Y2) * percAlongConnectingLine + Y1

    interpolatedDataPoint[1]["GWD"], interpolatedDataPoint[1]["GWS"] = from_vector(X3, Y3)
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
    print("\n")

    for i in numpy.linspace(0, len(GPS)-1, num=(len(GPS))):
        percX, percY = getPointRelPos(GPS[int(i)], sotonLatLong, brambleLatLong)
        percDiff = numpy.abs(100 * (percY - percX))
        percAve = (percX + percY) / 2
        if (percDiff < 1e-6):
            try:
                interpolatedDataPoint = interpolateData(sotonAlignedData[int(i)], brambleAlignedData[int(i)], percAve)
                GPS[int(i)][1]['GWS'] = interpolatedDataPoint[1]['GWS']
                GPS[int(i)][1]['GWD'] = interpolatedDataPoint[1]['GWD']
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

def addSpeedAndDirToGPS(GPS, Mag, accel, gyro):
    from math import atan2
    from math import sqrt, degrees
    from numpy import mean
    import sys
    index = 0
    utmOld = None
    utmNew = None
    for i in GPS:
        if index == 0 or index == 1 or index == 2:
            GPS[index][1]["COG"] = 0
            GPS[index][1]["SOG"] = 0
            GPS[index][1]["HDG"] = 0
            GPS[index][1]["GYRX"] = 0
            GPS[index][1]["GYRY"] = 0
            GPS[index][1]["GYRZ"] = 0
            GPS[index][1]["ACCX"] = 0
            GPS[index][1]["ACCY"] = 0
            GPS[index][1]["ACCZ"] = 0
            utmOld = [i[1]["Easting"], i[1]["Northing"]]
            tOld = i[0]
        else:
            utmNew = [i[1]["Easting"], i[1]["Northing"]]
            tNew = i[0]

            dt = tNew - tOld
            ds = sqrt((utmNew[0] - utmOld[0]) ** 2 + (utmNew[1] - utmOld[1]) ** 2)
            Speed = (ds / dt) / 0.5144

            GPSDirection = atan2((utmNew[0] - utmOld[0]), (utmNew[1] - utmOld[1]))
            #mag
            idx, _ = bisect(i[0], Mag)
            maglst = []
            for val in Mag[idx-50:idx+50]:
                maglst.append(val[1])
            MagAve = mean(maglst)
            # Gyro
            idx, _ = bisect(i[0], gyro)
            gyr_x, gyr_y, gyr_z = [], [], []
            for val in gyro[idx - 100:idx + 100]:
                gyr_x.append(val[1][0])
                gyr_y.append(val[1][1])
                gyr_z.append(val[1][2])
            gyr_x = mean(gyr_x)
            gyr_y = mean(gyr_y)
            gyr_z = mean(gyr_z)
            # accel
            idx, _ = bisect(i[0], accel)
            acc_x, acc_y, acc_z = [], [], []
            for val in accel[idx - 50:idx + 50]:
                acc_x.append(val[1][0])
                acc_y.append(val[1][1])
                acc_z.append(val[1][2])
            acc_x = mean(acc_x)
            acc_y = mean(acc_y)
            acc_z = mean(acc_z)

 # mag 100 gyro 200 accel 100

            GPS[index][1]["COG"] = Wrapto0_360(degrees(GPSDirection))
            GPS[index][1]["SOG"] = Speed
            GPS[index][1]["HDG"] = Wrapto0_360(MagAve + 160)
            GPS[index][1]["GYRX"] = gyr_x
            GPS[index][1]["GYRY"] = gyr_y
            GPS[index][1]["GYRZ"] = gyr_z
            GPS[index][1]["ACCX"] = acc_x
            GPS[index][1]["ACCY"] = acc_y
            GPS[index][1]["ACCZ"] = acc_z

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
    if x > 360:
        x -= 360
    return x


def Wrapto180(x):
    x = Wrapto0_360(x)
    if x > 180:
        x = 360 - x
    return x


def wraptopm180(x):
    x = Wrapto0_360(x)
    if x > 180:
        x -= 360
    return x


def addApparentWind(GPSWindHead):
    import sys
    index = 0
    for i in GPSWindHead:
        if index == 0:
            i[1]['TWA'] = None
            i[1]['COW'] = None
            i[1]['BSP'] = None
            i[1]['TWD'] = None
            i[1]['TWS'] = None
            i[1]['LWY'] = None
            i[1]['HDG'] = None
            i[1]['AWS'] = None
            i[1]['AWA'] = None
        else:
            try:
                X, Y= to_vector(i[1]['COG'], i[1]['SOG']); X1, Y1 = to_vector(i[1]['TDD'], i[1]['TDS'])
                i[1]['COW'], i[1]['BSP'] = from_vector(X+X1, Y+Y1)
                X, Y = to_vector(Wrapto0_360(i[1]['GWD']+180), i[1]['GWS']); X1, Y1 = to_vector(i[1]['TDD'], i[1]['TDS'])
                temp, i[1]['TWS'] = from_vector(X + X1, Y + Y1)
                i[1]['TWD'] = Wrapto0_360(temp - 180)
                i[1]['TWA'] = wraptopm180(i[1]['COW'] - i[1]['TWD'])
                i[1]['LWY'] = Wrapto180(i[1]['HDG'] - i[1]['COW'])
                X, Y = to_vector(Wrapto0_360(i[1]['TWD']+180), i[1]['TWS']); X1, Y1 = to_vector(i[1]['COW'], i[1]['BSP'])
                temp, i[1]['AWS'] = from_vector(X + X1, Y + Y1)
                i[1]['AWA'] = Wrapto180(temp+180)
            except KeyError:
                print('\nSomething not found in: ' + str(i)+'\n')

        sys.stdout.write("\rApparent Wind Speed and Direction: Processed GPS Point: {:,.0f} of {:,.0f}. "
                         .format(index + 1, len(GPSWindHead)))
        sys.stdout.flush()

        index += 1

    print('\r\nComplete.\r\n')
    return GPSWindHead


def to_vector(ang, stren):
    from math import cos, sin, radians
    Y = cos(radians(float(ang))) * float(stren)
    X = sin(radians(float(ang))) * float(stren)
    return X, Y


def from_vector(X, Y):
    from math import sqrt, atan2, degrees
    stren = sqrt(X*X+Y*Y)
    ang = Wrapto0_360(degrees(atan2(X, Y)))
    return ang, stren


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
            return correctedIndex, iterations
    import warnings
    warnings.warn('\nNo match found in bisect method\n')
    return correctedIndex, iterations


def data_save(data, file='Data_Save'):
    import json
    print('Saving Dictionary to File')
    file += '.json'
    with open(file, 'w') as out_file:
        js = json.dumps(data)
        out_file.write(js)
    return None


def Add_Tide(data):
    for i in data:
        i[1]['TDS'] = 1.5
        i[1]['TDD'] = 135
    return data


def Add_Tide2(data, HT='10:00', R=4.2):
    import csv
    import utm
    lists = []
    with open('Tide_DB.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for line in reader:
            lists.append(line)
    lists.pop(1); lists.pop(0)
    for i in lists:
        [Easting, Northing, _, _] = utm.from_latlon(float(i[0]), float(i[1]))
        i[0] = Easting; i[1] = Northing



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
            print('Saved Data Found \nStarting from Data_Save.json \n \n')
            return data
    except (NameError, FileNotFoundError):
        print('No Processed Saved Data Found \nStarting from log.txt \n \n')
        Mag, Gyro, GPS, Accel, Lin_Accel = sensor_log_read(input)
        data = getWindData(GPS)
        data = addSpeedAndDirToGPS(data, Mag, Lin_Accel, Gyro)
        data = Add_Tide(data)
        data = addApparentWind(data)
        data_save(data)
        print('-++'*30, '\nSaving Processed Data For Future use as', file, '.JSON \n', '-++'*30)
        return data


def data_time_trim(data, tmin, tmax):
    data2 = []
    for i in data:
        if i[0] < tmin or i[0] > tmax:
            None
        else:
            data2.append(i)
    return data2


def Manual_var_Adjust(data, keys, add, isit360=False, isit180=False):
    if type(keys) is not list:
        keys = [keys]
    for key in keys:
        if isit360:
            for i in data:
                i[0][key] = Wrapto0_360(i[0][key]+add)
        if isit180:
            for i in data:
                i[0][key] = Wrapto180(i[0][key]+add)
    return data


if __name__ == "__main__":
    data = PP_data_import(reprocess=True)
    from Plotting_ToolBox import linar_var_plot, GPS_plot
    # good upwind segment here
    #data = data_time_trim(data, 1479042400, 1479043500)
    linar_var_plot(data, ['TWS'])
    from polarPlotTools import plotPolars
    plotPolars(data,windSpeed=12.5, WindTol=3,anglerange=20, bodge=13)
    GPS_plot(data)
    import matplotlib.pyplot
    matplotlib.pyplot.show()




