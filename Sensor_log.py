def sensor_log_read(input):
    import csv
    import json
    with open(input) as csvfile:
        print('Opened File', input)
        next(csvfile)  # skip headings
        reader = csv.reader(csvfile, delimiter='\n')
        Magnetic = []
        Gyro = []
        GPS = []
        Accel = []
        Lin_Accel = []
        for a in reader:
            if 'Magnetic' in a[0]:
                b = a[0].split("|")
                Magnetic.append([float(b[3]), json.loads(b[2])])
            if 'Gyro' in a[0]:
                b = a[0].split("|")
                Gyro.append([float(b[3])/1000, json.loads(b[2])])
            if 'GPS' in a[0]:
                b = a[0].split("|")
                GPS.append([float(b[3])/1000, json.loads(b[2])])
            if 'Acceleration' in a[0] and 'Linear' not in a[0]:
                b = a[0].split("|")
                Accel.append([int(b[3])/1000, json.loads(b[2])])
            if 'Linear Acceleration' in a[0]:
                b = a[0].split("|")
                Lin_Accel.append([float(b[3])/1000, json.loads(b[2])])
    print('Closed:', input)
    GPS = GPS_Data_Tidy(GPS)
    print('Magn Data points:', len(Magnetic))
    freq_out(Magnetic)
    print('Gyro Data points:', len(Gyro))
    freq_out(Gyro)
    print('GPS Data points:', len(GPS))
    freq_out(GPS)
    print('Lin_Accel Data points:', len(Lin_Accel))
    freq_out(Lin_Accel)
    Magnetic = Mag_Data_Tidy(Magnetic)
    return Magnetic, Gyro, GPS, Accel, Lin_Accel


def freq_out(data):
    from statistics import mean
    gap = []
    if len(data) < 501:
        print('Data to short')
        return None
    for i in range(500):
        t0 = (data[i][0])
        t1 = (data[i+1][0])
        gap.append(t1-t0)
    ave = mean(gap)
    freq = 1/ave
    print('Frequency: ', round(freq,1), 'Hz')
    return None


def GPS_Data_Tidy(GPS):
    print('Proccesing GPS data')
    import utm
    new_GPS = []
    idx = -1
    for i in GPS:
        t = i[1]['mTime']/1000
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
    print('Proccesing mag data')
    import math
    new_mag = []
    for i in Mag:
        time = i[0]
        ang = math.atan2(i[1][1], i[1][0])
        ang *= 180/(2*math.pi)
        if ang < 0:
            ang += 180
            None
        new_mag.append([time, ang])
    return new_mag


def XYZ_plot(data, mag=False):
    import matplotlib.pyplot as plt
    time, x, y, z, mag = [], [], [], [], []
    for i in data:
        time.append(i[0])
        x.append(i[1][0])
        y.append(i[1][1])
        z.append(i[1][2])
        if mag:
            mag.append((i[1][0]**2+i[1][1]**2+i[1][2]**2)**0.5)
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
    import matplotlib.pyplot as plt
    time,  y = [], []
    for i in data:
        time.append(i[0])
        y.append(i[1][idx])
    plt.plot(time, y, 'bx', label='Y')
    plt.legend()
    plt.xlabel("Time (unix seconds)")
    plt.grid(True)
    return time, y


def Mag_plot(data):
    import matplotlib.pyplot as plt
    time, phi = [], []
    for i in data:
        time.append(i[0])
        phi.append(i[1])
    plt.plot(time, phi, 'rx', label='phi')
    plt.legend()
    plt.xlabel("UnixTime stamp [s]")
    plt.ylabel("Heading [º]")
    plt.grid(True)


def GPS_plot(data):
    import matplotlib.pyplot as plt
    time, north, east, acc = [], [], [], []
    for i in data:
        time.append(i[0])
        acc.append(i[1]['Accuracy']/2)
        east.append(i[1]['Easting'])
        north.append(i[1]['Northing'])
    plt.errorbar(east, north, xerr=acc, yerr=acc, label='GPS', ecolor='b', color='k', marker='o')
    plt.legend()
    plt.xlabel("East [m]")
    plt.ylabel("North [m]")
    plt.grid(True)
    plt.axis('equal')


def GPS_speed_plot(data):
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
    for i in range(len(data)-1):
        Ediff = east[i] - east[i+1]
        Ndiff = north[i] - north[i+1]
        hyp = (Ediff**2+Ndiff**2)**0.5
        timediff = (time[i+1]-time[i])
        times.append(time[i])
        speeds.append((hyp/timediff)/0.514)
    speed_ave = movingaverage(speeds, 7)
    plt.plot(times, speeds, 'b', label='RAW')
    plt.plot(times, speed_ave, 'r',  label='7pt moving_ave')
    plt.legend()
    plt.xlabel("UnixTime [s]")
    plt.ylabel("Speed [knts]")
    plt.grid(True)
    print('Max Speed (RAW)=', max(speeds), 'knts')
    print('Max Speed (7pt moving ave)=', max(speed_ave), 'knts')


def integrator(y, time):
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
    import numpy
    window = numpy.ones(int(window_size))/float(window_size)
    temp = numpy.convolve(interval, window, 'same')
    return numpy.ndarray.tolist(temp)


if __name__ == "__main__":
    [Mag, Gyro, GPS, Accel, Lin_Accel] = sensor_log_read('log.txt')
    import matplotlib.pyplot as plt
    plt.figure(1)
    GPS_plot(GPS)
    plt.figure(2)
    GPS_speed_plot(GPS)
    plt.figure(3)
    Mag_plot(Mag)
    plt.figure(4)
    XYZ_plot(Lin_Accel)
    #
    # [Time, Y] = Y_plot(Lin_Accel)
    # Y = movingaverage(Y, 50)
    # integrator(Y, Time)
    plt.show()

