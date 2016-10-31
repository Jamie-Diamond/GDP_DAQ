

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
            if 'Acceleration' in a[0]:
                b = a[0].split("|")
                Accel.append([int(b[3]), json.loads(b[2])])
        print('Magn Data points:', len(Magnetic))
        print('Gyro Data points:', len(Gyro))
        print('GPS Data points:', len(GPS))
        print('Accel Data points:', len(Accel))
    GPS = GPS_Data_Tidy(GPS)
    return Magnetic, Gyro, GPS, Accel

def GPS_Data_Tidy(GPS):
    new_GPS = []
    for i in GPS:
        t = i[1]['mTime']
        ac = i[1]['mAccuracy']
        lon = i[1]['mLongitude']
        lat = i[1]['mLatitude']
        new_GPS.append([t, {'Accuracy': ac, 'Longitude': lon, 'Latitude': lat}])
    return new_GPS


if __name__ == "__main__":
    [Mag, Gyro, GPS, Accel] = sensor_log_lists('sensor_log1.txt')
    print(Mag)
    print(Gyro)
    print(GPS)
    print(Accel)


