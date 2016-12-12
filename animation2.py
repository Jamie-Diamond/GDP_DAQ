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
    data = None                         # Input data is as a list of dictionaries, one dictionary for each line to draw. Each dictionary needs to contain: "name" "x_data" "y_data"
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
            self.ax.set_xlim(self.data[0]["x_data"][0], self.data[0]["x_data"][self.data_trail])
        if self.data_y_lim != None:
            self.ax.set_ylim(self.data_y_lim[0], self.data_y_lim[1])
        else:
            min_y = []
            max_y = []

            for i in self.data:
                min_y.append(math.floor(min(i["y_data"])))
                max_y.append(math.ceil(max(i["y_data"])))

            self.ax.set_ylim(min(min_y), max(max_y))

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
            self.data_x_lim = [self.data[0]["x_data"][low_index], self.data[0]["x_data"][high_index]]

        self.ax.clear()
        self.set_up()

        if self.graph_type == "Line" or self.graph_type == "line":
            for i in self.data:
                self.ax.plot(i["x_data"][low_index:high_index], i["y_data"][low_index:high_index], label=i["name"])

            self.ax.legend()
        else:
            for i in self.data:
                self.ax.scatter(i["x_data"][low_index:high_index], i["y_data"][low_index:high_index], label=i["name"])

            self.ax.legend()

    def run(self):
        self.set_up()
        animation = FuncAnimation(self.fig, self.update, interval=self.interval)
        plt.show()

### Everything below here is just showing that it works

import random
x = []
y1 = []
y2 = []
y3 = []
y4 = []

r1 = random.random()
r2 = random.random()
r3 = random.random()
r4 = random.random()

no_datapoints = 8000
random_var = 0.1

for i in range(no_datapoints):
    x.append(i)

for i in x:
    y1.append(r1*( math.sin(math.radians(4 * i)) + random_var * (2 * numpy.random.random() - 1)))
    y2.append(r2*( math.cos(math.radians(4 * i)) + random_var * (2 * numpy.random.random() - 1)))
    y3.append(r3*(-math.sin(math.radians(4 * i)) + random_var * (2 * numpy.random.random() - 1)))
    y4.append(r3*(-math.cos(math.radians(4 * i)) + random_var * (2 * numpy.random.random() - 1)))


anim = animatePlot()
anim.data = [
    {"name": "random sin", "x_data": x, "y_data": y1},
    {"name": "random cos", "x_data": x, "y_data": y2},
    {"name": "random -sin", "x_data": x, "y_data": y3},
    {"name": "random -cos", "x_data": x, "y_data": y4}]
#anim.data_x_lim = [0, no_datapoints]
#anim.data_y_lim = [-5, 5]
anim.points_per_second = 100
anim.data_trail = 360
anim.graph_type = "line"
anim.run()