from sensor_log_ToolBox import data_import
from windDataTools import getWindData
from boatHeadingTools import addSpeedAndDirToGPS
from math import cos
import sys
import matplotlib.pyplot

def addApparentWind(GPSWindHead):
    index = 0
    for i in GPSWindHead:
        if index == 0:
            i[1]['AWA'] = None
            i[1]['AWS'] = None
            i[1]['TWA'] = None
        else:
            try:
                i[1]['TWA'] = i[1]['HDG'] - i[1]['GWD']
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

def polarFilter(Data, angleRange):
    index = 0;
    polarPoints = []
    for i in Data:
        if index > 3 and index < len(Data) - 2:
            if abs(i[1]["HDG"] - Data[index - 2][1]["HDG"]) < angleRange \
            and abs(i[1]["HDG"] - Data[index - 1][1]["HDG"]) < angleRange \
            and abs(i[1]["HDG"] - Data[index + 1][1]["HDG"]) < angleRange \
            and abs(i[1]["HDG"] - Data[index + 2][1]["HDG"]) < angleRange:
                #print(abs(i[1]["HDG"] - Data[index - 2][1]["HDG"]), abs(i[1]["HDG"] - Data[index - 1][1]["HDG"]), abs(i[1]["HDG"] - Data[index + 1][1]["HDG"]), abs(i[1]["HDG"] - Data[index + 2][1]["HDG"]))
                polarPoints.append(i)

        index += 1

    return polarPoints

def linar_var_plot(Data, key='SOG',windSpeed=15, error=15):
    var = []
    time = []
    for i in Data:
        if i[1]["GWS"] is not None:
            temp = abs(i[1]["GWS"] - windSpeed)
            if temp < error:
                var.append(i[1][key])
                time.append(i[0])
    matplotlib.pyplot.plot(time, var,'x')
    matplotlib.pyplot.show()


def plotPolars(Data, windSpeed=15, error=15):
    theta = []
    r = []
    for i in Data:
        if i[1]["GWS"] is not None:
            var = abs(i[1]["GWS"] - windSpeed)
            if var < error:
                theta.append(i[1]["TWA"])
                r.append(i[1]["SOG"])

    axis = matplotlib.pyplot.subplot(111, projection='polar')
    axis.set_theta_zero_location('N')
    axis.set_theta_direction(-1)
    axis.set_rlabel_position(90)
    axis.plot(theta, r, '+b')
    axis.grid(True)
    axis.set_title("Boat Speed vs Wind Direction (Wind Speed: " + str(windSpeed) + "±" + str(error) + ")", va='bottom')
    matplotlib.pyplot.show()


Mag, Gyro, GPS, Accel, Lin_Accel = data_import()
GPSWind = getWindData(GPS)
GPSWindHead = addSpeedAndDirToGPS(GPSWind, Mag)


GPSWindAHead = addApparentWind(GPSWindHead)
#linar_var_plot(GPSWindAHead,'TWA', 13, 1)
matplotlib.pyplot.figure(2)
plotPolars(polarFilter(GPSWindAHead, 0.3), 13, 1)
