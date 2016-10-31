

def sensor_log_lists(input):
    import csv
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
                Magnetic.append([int(b[3]), b[2]])
            if 'Gyro' in a[0]:
                b = a[0].split("|")
                Gyro.append([int(b[3]), b[2]])
            if 'GPS' in a[0]:
                b = a[0].split("|")
                GPS.append([int(b[3]), b[2]])
            if 'Acceleration' in a[0]:
                b = a[0].split("|")
                Accel.append([int(b[3]), b[2]])
        print('Magn Data points:', len(Magnetic))
        print('Gyro Data points:',len(Gyro))
        print('GPS Data points:',len(GPS))
        print('Accel Data points:',len(Accel))
    return Magnetic, Gyro, GPS, Accel

if __name__ == "__main__":
    sensor_log_lists('sensor_log1.txt')
