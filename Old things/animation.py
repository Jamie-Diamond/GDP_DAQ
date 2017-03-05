"""
Rain simulation

Simulates rain drops on a surface by animating the scale and opacity
of 50 scatter points.

Author: Nicolas P. Rougier
"""
import numpy
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math

class animatePlot:
    data_x = None
    data_y = None
    data_x_label = None
    data_y_label = None
    data_x_lim = None                   # If you dont set data_x_lim it will automatically follow the graph as its plotted.
    data_y_lim = None                   # If you dont set data_y_lim it will automatically set it as the rounded min/max of the data.
    plot_type = "Linear"
    graph_type = "Scatter"
    points_per_second = None
    figure_number = 1
    interval = 100
    data_trail = 100

    # Don't change these
    fig = None;
    ax = None;
    ticks_per_second = None
    points_per_tick = None

    def set_up(self):
        # Create new figure and add axes
        self.fig = plt.figure(self.figure_number)
        if self.plot_type == "Polar" or self.plot_type == "polar":
            self.ax = self.fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
        else:
            self.ax = self.fig.add_axes([0.1, 0.1, 0.8, 0.8])

        if self.data_x_lim != None:
            self.ax.set_xlim(self.data_x_lim[0], self.data_x_lim[1])
        else:
            self.ax.set_xlim(self.data_x[0], self.data_x[self.data_trail])
        if self.data_y_lim != None:
            self.ax.set_ylim(self.data_y_lim[0], self.data_y_lim[1])
        else:
            self.ax.set_ylim(math.floor(min(self.data_y)), math.ceil(max(self.data_y)))
        if self.data_x_label != None:
            self.ax.set_xlabel(self.data_x_label)
        if self.data_y_label != None:
            self.ax.set_ylabel(self.data_y_label)

        self.ticks_per_second = 1000 / self.interval
        self.points_per_tick = int(self.points_per_second / self.ticks_per_second)

    def update(self, frame_number):
        high_index = self.points_per_tick * frame_number

        if self.data_trail > self.points_per_tick * frame_number:
            low_index = 0
        else:
            low_index = self.points_per_tick * frame_number - self.data_trail
            self.data_x_lim = [self.data_x[low_index], self.data_x[high_index]]

        self.ax.clear()
        self.set_up()

        if self.graph_type == "Line" or self.graph_type == "line":
            line = self.ax.plot(self.data_x[low_index:high_index], self.data_y[low_index:high_index])
        else:
            scat = self.ax.scatter(self.data_x[low_index:high_index], self.data_y[low_index:high_index])

    def run(self):
        self.set_up()
        animation = FuncAnimation(self.fig, self.update, interval=self.interval)
        plt.show()


x = []
y1 = []
y2 = []
no_datapoints = 8000

for i in range(no_datapoints):
    x.append(i)

for i in x:
    y1.append(math.sin(math.radians(4*i)) + 0.1 * (2 * numpy.random.random() - 1))

for i in x:
    y2.append(math.cos(math.radians(4 * i)) + 0.1 * (2 * numpy.random.random() - 1))

anim1 = animatePlot()
anim1.data_x = x
anim1.data_y = y1
#anim.data_x_lim = [0, no_datapoints]
#anim.data_y_lim = [-5, 5]
anim1.points_per_second = 100
anim1.data_trail = 360
anim1.graph_type = "line"
anim1.run()


# # Create new Figure and an Axes which fills it.
# fig = plt.figure(figsize=(7,7))
# ax = fig.add_axes([0, 0, 1, 1], frameon=False)
# ax.set_xlim(0,1), ax.set_xticks([])
# ax.set_ylim(0,1), ax.set_yticks([])
#
# # Create rain data
# n_drops = 50
# rain_drops = np.zeros(n_drops, dtype=[('position', float, 2),
#                                       ('size',     float, 1),
#                                       ('growth',   float, 1),
#                                       ('color',    float, 4)])
#
# # Initialize the raindrops in random positions and with
# # random growth rates.
# rain_drops['position'] = np.random.uniform(0, 1, (n_drops, 2))
# rain_drops['growth'] = np.random.uniform(50, 200, n_drops)
#
# # Construct the scatter which we will update during animation
# # as the raindrops develop.
# scat = ax.scatter(rain_drops['position'][:,0], rain_drops['position'][:,1],
#                   s=rain_drops['size'], lw=0.5, edgecolors=rain_drops['color'],
#                   facecolors='none')
#
#
# def update(frame_number):
#     # Get an index which we can use to re-spawn the oldest raindrop.
#     current_index = frame_number % n_drops
#
#     # Make all colors more transparent as time progresses.
#     rain_drops['color'][:, 3] -= 1.0/len(rain_drops)
#     rain_drops['color'][:,3] = np.clip(rain_drops['color'][:,3], 0, 1)
#
#     # Make all circles bigger.
#     rain_drops['size'] += rain_drops['growth']
#
#     # Pick a new position for oldest rain drop, resetting its size,
#     # color and growth factor.
#     rain_drops['position'][current_index] = np.random.uniform(0, 1, 2)
#     rain_drops['size'][current_index] = 5
#     rain_drops['color'][current_index] = (0, 0, 0, 1)
#     rain_drops['growth'][current_index] = np.random.uniform(50, 200)
#
#     # Update the scatter collection, with the new colors, sizes and positions.
#     scat.set_edgecolors(rain_drops['color'])
#     scat.set_sizes(rain_drops['size'])
#     scat.set_offsets(rain_drops['position'])
#
#
# # Construct the animation, using the update function as the animation
# # director.
# animation = FuncAnimation(fig, update, interval=10)
# plt.show()