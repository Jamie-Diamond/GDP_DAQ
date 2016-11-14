import urllib2
import csv
import datetime


def getDayWindData(GPS, loc):
    listData = []
    timeStamp1 = GPS[0][0]
    url = createurl(loc, timeStamp1)
    if url != False:
        print("Data retrieved from: " + url)
        response = urllib2.urlopen(url)
        data = csv.reader(response)
        for row in data:
            listData.append(row)
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
    return str(roundNo(fromStamp.strftime('%M'))), \
           fromStamp.strftime('%M'), \
           fromStamp.strftime('%H'), \
           fromStamp.strftime('%d'), \
           fromStamp.strftime('%b'), \
           fromStamp.strftime('%B'), \
           fromStamp.strftime('%Y')


def roundNo(x, base=5):
    return int(base * round(float(x) / base))


def alignGPSTimeAndWindData(GPS, rawWind):
    alignedData = []
    for i in GPS:
        timeStamp = i[0]
        rmin, min, hour, day, sMonth, lMonth, year = convertTimeStamp(timeStamp)
        time = "%02d:%02d" % (int(hour), int(rmin))
        for j in rawWind:
            if j[1] == time:
                alignedData.append([timeStamp, {
                    "Wind Speed": j[2],
                    "Wind Dir": j[3],
                    "Wind Gust": j[4]
                }])
    return alignedData

def getWindData(GPS):
    sotonWindData = getDayWindData(GPS, "Soton")
    brambleWindData = getDayWindData(GPS, "Bramble")
    #cowesWindData = getDayWindData(GPS, "Cowes")

    sotonAlignedData = alignGPSTimeAndWindData(GPS, sotonWindData)
    brambleAlignedData = alignGPSTimeAndWindData(GPS, brambleWindData)
    #cowesAlignedData = alignGPSTimeAndWindData(GPS, cowesWindData)

    print("Soton data:")
    for data in sotonAlignedData:
        print data
    print("Bramble data: ")
    for data in brambleAlignedData:
        print data
    # print("Cowes data: ")
    # for data in brambleAlignedData:
    #     print data

    return True

getWindData([[1479049200]])