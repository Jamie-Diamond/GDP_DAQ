class KalmanFilter(object):

    def __init__(self, process_variance, estimated_measurement_variance):
        self.process_variance = process_variance
        self.estimated_measurement_variance = estimated_measurement_variance
        self.posteri_estimate = 0.0
        self.posteri_error_estimate = 1.0

    def input_latest_noisy_measurement(self, measurement):
        priori_estimate = self.posteri_estimate
        priori_error_estimate = self.posteri_error_estimate + self.process_variance

        blending_factor = priori_error_estimate / (priori_error_estimate + self.estimated_measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

    def get_latest_estimated_measurement(self):
        return self.posteri_estimate

def gpx_spd_karman(name):
    import  gpxpy
    import matplotlib.pyplot as plt
    import utm
    import random
    from CSV_GPX_Tools import movingaverage
    with open(name) as gpx_one:
        gpx_one = gpxpy.parse(gpx_one)
        a=0
        for track in gpx_one.tracks:
            a+=1
            longs = []
            times = []
            lats = []
            for segment in track.segments:
                for point in segment.points:
                    lats.append(point.latitude)
                    longs.append(point.longitude)
                    times.append(point.time)
    # Filter here #######################
    # in practice we would take our sensor, log some readings and get the
    # standard deviation
    import numpy
    iteration_count = len(longs)
    measurement_standard_deviation = numpy.std([random.random() * 2.0 - 1.0 for j in range(iteration_count)])

    # The smaller this number, the fewer fluctuations, but can also venture off
    # course...
    process_variance = 1e-10
    estimated_measurement_variance = measurement_standard_deviation ** 2  # 0.05 ** 2

    posteri_estimate_graph_lats = []
    posteri_estimate_graph_longs = []

    kalman_filter = KalmanFilter(process_variance, estimated_measurement_variance)
    for iteration in range(1, iteration_count):
        kalman_filter.input_latest_noisy_measurement(lats[iteration])
        posteri_estimate_graph_lats.append(kalman_filter.get_latest_estimated_measurement())
    kalman_filter = KalmanFilter(process_variance, estimated_measurement_variance)
    for iteration in range(1, iteration_count):
        kalman_filter.input_latest_noisy_measurement(longs[iteration])
        posteri_estimate_graph_longs.append(kalman_filter.get_latest_estimated_measurement())
    # #######################

    plt.plot(longs, lats, color='b', label='Raw')
    plt.plot(posteri_estimate_graph_longs, posteri_estimate_graph_lats, color='r', label='Karman Filtered')
    plt.legend()
    plt.show
    print(posteri_estimate_graph_longs)
    print(longs)
    print(posteri_estimate_graph_lats)
    print(lats)

    distances = []
    speeds = []
    i = 0
    duration = [0]
    timediff_lst = []
    for i in (range(len(lats)-1)):
        [lat, long, _, _] = utm.from_latlon(lats[i], longs[i])
        [lat1, long1, _, _] = utm.from_latlon(lats[i+1], longs[i+1])
        latdiff = lat - lat1
        longdiff = long - long1
        time0 = times[i]
        time1 = times[i+1]
        timediff = time1 - time0
        timediff_lst.append(timediff)
        duration.append(timediff.total_seconds() + duration[-1])
        dist = latdiff**2 + longdiff**2
        dist **= 0.5
        distances.append(dist)
        speed = dist/timediff.total_seconds()
        speeds.append(speed)

    del duration[0]
    print(numpy.mean(timediff_lst))

    print(len(speeds))
    print(len(duration))
    if 'garmin' in name:
        x = 1
    else:
        x = 6
    speeds_ave = movingaverage(speeds, x)

    return speeds_ave, duration

if __name__ == "__main__":
    [ps, pd] = gpx_spd_karman('cycle_in.gpx')