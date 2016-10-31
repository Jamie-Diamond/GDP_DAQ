def sensor_log_lists(input):
    import csv
    import json
    with open(input) as csvfile:
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
                Magnetic.append([int(b[3]), json.loads(b[2])])
            if 'Gyro' in a[0]:
                b = a[0].split("|")
                Gyro.append([int(b[3]), json.loads(b[2])])
            if 'GPS' in a[0]:
                b = a[0].split("|")
                GPS.append([int(b[3]), json.loads(b[2])])
            if 'Acceleration' in a[0] and 'Linear' not in a[0]:
                b = a[0].split("|")
                Accel.append([int(b[3]), json.loads(b[2])])
            if 'Linear Acceleration' in a[0]:
                b = a[0].split("|")
                Lin_Accel.append([int(b[3]), json.loads(b[2])])
        print('Magn Data points:', len(Magnetic))
        print('Gyro Data points:', len(Gyro))
        print('GPS Data points:', len(GPS))
        print('Accel Data points:', len(Accel))
    GPS = GPS_Data_Tidy(GPS)
    Magnetic = Mag_Data_Tidy(Magnetic)
    return Magnetic, Gyro, GPS, Accel, Lin_Accel


def GPS_Data_Tidy(GPS):
    import utm
    new_GPS = []
    for i in GPS:
        t = i[1]['mTime']
        ac = i[1]['mAccuracy']
        lon = i[1]['mLongitude']
        lat = i[1]['mLatitude']
        [Easting, Northing, _, _] = utm.from_latlon(lat, lon)
        new_GPS.append([t, {'Accuracy': ac, 'Easting': Easting, 'Northing': Northing}])
    return new_GPS


def Mag_Data_Tidy(Mag):
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


def XYZ_plot(data):
    import matplotlib.pyplot as plt
    time, x, y, z, mag = [], [], [], [], []
    for i in data:
        time.append(i[0])
        x.append(i[1][0])
        y.append(i[1][1])
        z.append(i[1][2])
        mag.append((i[1][0]**2+i[1][1]**2+i[1][2]**2)**0.5)
    plt.plot(time, x, 'rx-', label='X')
    plt.plot(time, y, 'bx-', label='Y')
    plt.plot(time, z, 'k*-', label='Z')
    plt.plot(time, mag, 'g+-', label='Magnitude')
    plt.legend()
    plt.xlabel("Time (unix seconds)")
    plt.ylabel("Force [N]")
    plt.grid(True)
    plt.show()


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
    plt.show()


def GPS_plot(data):
    import matplotlib.pyplot as plt
    time, north, east, acc = [],[],[],[]
    for i in data:
        time.append(i[0])
        acc.append(i[1]['Accuracy'])
        east.append(i[1]['Easting'])
        north.append(i[1]['Northing'])
    plt.errorbar(east, north, xerr=acc, yerr=acc, label='GPS', ecolor='b', color='k', marker='o')
    plt.legend()
    plt.xlabel("")
    plt.ylabel("")
    plt.grid(True)
    plt.axis('equal')
    plt.show()


if __name__ == "__main__":
    [Mag, Gyro, GPS, Accel, Lin_Accel] = sensor_log_lists('sensor_log2.txt')
    GPS_plot(GPS)
    #Mag_plot(Mag)
    #XYZ_plot(Lin_Accel)
    #XYZ_plot(Accel)

