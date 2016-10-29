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

def lat_long_karman(lats, longs):
    import numpy
    import random
    # Filter here #######################
    # in practice we would take our sensor, log some readings and get the
    # standard deviation
    iteration_count = len(longs)
    measurement_standard_deviation = numpy.std([random.random() * 0.0000001 for j in range(iteration_count)])

    # The smaller this number, the fewer fluctuations, but can also venture off
    # course...
    process_variance = 1e-5
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
    return posteri_estimate_graph_lats, posteri_estimate_graph_longs



if __name__ == "__main__":
    from CSV_GPX_Tools import gpx_lat_long_duration
    import matplotlib.pyplot as plt
    [lats, longs, times] = gpx_lat_long_duration('cycle_in.gpx')
    [latsK, longsK] = lat_long_karman(lats, longs)
    plt.plot(longs, lats, 'bo', label='Raw')
    plt.plot(longsK, latsK, 'rx', label='Karman Filtered')
    plt.legend()
    plt.show()
