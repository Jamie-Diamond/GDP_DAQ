from sensor_log_ToolBox import sensor_log_read
from windDataTools import getWindData
from boatHeadingTools import addSpeedAndDirToGPS
from math import cos
import sys
import matplotlib.pyplot




def addApparentWind(GPSWindHead):
    index = 0
    for i in GPSWindHead:
        if index == 0:
            i[1]['App Wind Dir'] = None
            i[1]['App Wind Speed'] = None
        else:
            try:
                i[1]['Wind Dir'] = i[1]['Heading'] - i[1]['Wind Dir']
                i[1]['App Wind Dir'] = None ####################### Add Equation here ########################
                i[1]['App Wind Speed'] = None#i[1]['Wind Speed']*cos(i[1]['App Wind Dir'])
            except KeyError:
                print('Something not found in: ' + str(i))

        sys.stdout.write("\rApparent Wind Speed and Direction: Processed GPS Point: {:,.0f} of {:,.0f}. "
                         .format(index + 1, len(GPSWindHead)))
        sys.stdout.flush()

        index += 1

    print('\r\nComplete.\r\n')
    return GPSWindHead

def speed_plot(Data):
    speed = []
    time = []
    for i in Data:
        speed.append(i[1]["Speed"])
        time.append(i[0])
    matplotlib.pyplot.plot(time, speed,'x')
    #matplotlib.pyplot.show()



def plotPolars(Data, windSpeed=0, error=360):
    theta = []
    r = []

    for i in Data:
        if i[1]["Wind Speed"] != None:
            var = abs(i[1]["Wind Speed"] - windSpeed)
            if var < error:
                theta.append(i[1]["Wind Dir"])
                r.append(i[1]["Speed"])

    axis = matplotlib.pyplot.subplot(111, projection='polar')
    axis.set_theta_zero_location('N')
    axis.set_theta_direction(-1)
    axis.set_rlabel_position(90)
    axis.plot(theta, r, 'rx')
    axis.grid(True)

    axis.set_title("Boat Speed vs Wind Direction (Wind Speed: " + str(windSpeed) + "±" + str(error) + ")", va='bottom')
    matplotlib.pyplot.show()

Mag, Gyro, GPS, Accel, Lin_Accel = sensor_log_read('log.txt')
GPSWind = getWindData(GPS)
GPSWindHead = addSpeedAndDirToGPS(GPSWind, Mag)
speed_plot(GPSWindHead)
matplotlib.pyplot.figure(2)
GPSWindAHead = addApparentWind(GPSWindHead)
plotPolars(GPSWindAHead, 13, 5)


