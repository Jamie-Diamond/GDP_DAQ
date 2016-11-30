def XYZ_plot(data, mag=False):
    ''' takes data in standard format and plots XYZ on same graph against time, if mag True plots magnitude of XYZ'''
    import matplotlib.pyplot as plt
    time, x, y, z, mag = [], [], [], [], []
    for i in data:
        time.append(i[0])
        x.append(i[1][0])
        y.append(i[1][1])
        z.append(i[1][2])
        if mag:
            mag.append((i[1][0] ** 2 + i[1][1] ** 2 + i[1][2] ** 2) ** 0.5)
    plt.plot(time, x, 'rx-', label='X')
    plt.plot(time, y, 'bx-', label='Y')
    plt.plot(time, z, 'k*-', label='Z')
    if mag:
        plt.plot(time, mag, 'g+-', label='Magnitude')
    plt.legend()
    plt.xlabel("Time (unix seconds)")
    plt.ylabel("Force [N]")
    plt.grid(True)


def Y_plot(data, idx=1):
    ''' just plots one series of data, depending on what idx '''
    import matplotlib.pyplot as plt
    time, y = [], []
    for i in data:
        time.append(i[0])
        y.append(i[1][idx])
    plt.plot(time, y, 'bx', label='Y')
    plt.legend()
    plt.xlabel("Time (unix seconds)")
    plt.grid(True)
    plt.show()
    return time, y


def Mag_plot(data):
    '''PLots magnetic data'''
    import matplotlib.pyplot as plt
    time, phi = [], []
    for i in data:
        time.append(i[0])
        phi.append(i[1])
    plt.plot(time, phi, 'rx', label='phi')
    plt.legend()
    plt.xlabel("UnixTime stamp [s]")
    plt.ylabel("Heading [deg]")
    plt.grid(True)
    plt.show()


def GPS_plot(data):
    '''Plots GPS data'''
    import matplotlib.pyplot as plt
    time, north, east, acc = [], [], [], []
    for i in data:
        time.append(i[0])
        try:
            acc.append(i[1]['Accuracy']/2)
        except KeyError:
            acc.append(0)
        east.append(i[1]['Easting'])
        north.append(i[1]['Northing'])
    plt.errorbar(east, north, xerr=acc, yerr=acc, label='GPS', ecolor='b', color='k', marker='o')
    plt.legend()
    plt.xlabel("East [m]")
    plt.ylabel("North [m]")
    plt.grid(True)
    plt.axis('equal')


def GPS_speed_plot(data):
    '''plots speed point 2 point and 7pt moving average'''
    speeds = []
    times = []
    time = []
    east = []
    north = []
    import matplotlib.pyplot as plt
    for i in data:
        time.append(i[0])
        east.append(i[1]['Easting'])
        north.append(i[1]['Northing'])
    for i in range(len(data) - 1):
        Ediff = east[i] - east[i + 1]
        Ndiff = north[i] - north[i + 1]
        hyp = (Ediff ** 2 + Ndiff ** 2) ** 0.5
        timediff = (time[i + 1] - time[i])
        times.append(time[i])
        speeds.append((hyp / timediff) / 0.514)
    speed_ave = movingaverage(speeds, 7)
    plt.plot(times, speeds, 'b', label='RAW')
    plt.plot(times, speed_ave, 'r', label='7pt moving_ave')
    plt.legend()
    plt.xlabel("UnixTime [s]")
    plt.ylabel("Speed [knts]")
    plt.grid(True)
    print('Max Speed (RAW)=', max(speeds), 'knts')
    print('Max Speed (7pt moving ave)=', max(speed_ave), 'knts')


def integrator(y, time):
    ''' integrate y data with respect to time return Y_int'''
    import matplotlib.pyplot as plt
    from scipy import integrate
    import numpy as np
    plt.subplot(2, 1, 1)
    plt.plot(time, y)
    yint = integrate.cumtrapz(y, time, initial=0)
    yint = np.ndarray.tolist(yint)
    plt.subplot(2, 1, 2)
    plt.plot(time, yint)
    plt.show()
    return yint


def movingaverage(interval, window_size):
    '''moving average function'''
    import numpy
    window = numpy.ones(int(window_size)) / float(window_size)
    temp = numpy.convolve(interval, window, 'same')
    return numpy.ndarray.tolist(temp)


def linar_var_plot(Data, key='SOG',windSpeed=15, error=15):
    import matplotlib
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

# to be moved to new file
# def getUserRequirement():
#     request = raw_input("What would you like? ").strip()
#
#     if request == "Y plot":
#         return Y_plot(Lin_Accel), getUserRequirement()
#     elif request == "Mag plot":
#         return Mag_plot(Mag), getUserRequirement()
#     elif request == "GPS plot":
#         return GPS_plot(GPS), getUserRequirement()
#     elif request == "End" or request == "end" or request == "Stop" or request == "stop" or request == "Close" or request == "close":
#         return True
#     else:
#         print("Request is not recognised try again."
#               "\r\nCommands:"
#               "\r\n - Y plot"
#               "\r\n - Mag Plot"
#               "\r\n - GPS Plot"
#               "\r\n - End"
#               "\r\n")
#         return getUserRequirement()



# if __name__ == "__main__":
#     #inputFile = input("What is the input filename? ")
#     #outputFile = input("What is the output filename? ")
#     [Mag, Gyro, GPS, Accel, Lin_Accel] = data_read()
#     import matplotlib.pyplot as plt
#     #getUserRequirement()
#
#     plt.figure(1)
#     GPS_plot(GPS)
#     plt.figure(2)
#     GPS_speed_plot(GPS)
#     from gpx_import import gpx_reader
#     garminGPS = gpx_reader('Garmin_TestSail_1.gpx')
#     plt.figure(3)
#     GPS_plot(garminGPS)
#     plt.figure(4)
#     GPS_speed_plot(garminGPS)
#     plt.show()

#Mag, Gyro, GPS, Accel, Lin_Accel = sensor_log_read('log.txt')
#windDataTools.getWindData(GPS)
