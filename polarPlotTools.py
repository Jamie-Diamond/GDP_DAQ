from Data_import import PP_data_import
from Plotting_ToolBox import linar_var_plot, GPS_plot
import matplotlib.pyplot


def polarFilter(Data, angleRange):
    index = 0
    polarPoints = []
    for i in Data:
        if index > 3 and index < len(Data) - 2:
            if abs(i[1]["HDG"] - Data[index - 2][1]["HDG"]) < angleRange \
            and abs(i[1]["HDG"] - Data[index - 1][1]["HDG"]) < angleRange \
            and abs(i[1]["HDG"] - Data[index + 1][1]["HDG"]) < angleRange \
            and abs(i[1]["HDG"] - Data[index + 2][1]["HDG"]) < angleRange:
                #print(abs(i[1]["HDG"] - Data[index - 2][1]["HDG"]), abs(i[1]["HDG"] - Data[index - 1][1]["HDG"]), abs(i[1]["HDG"] - Data[index + 1][1]["HDG"]), abs(i[1]["HDG"] - Data[index + 2][1]["HDG"]))
                polarPoints.append(i)

        index += 1

    return polarPoints


def plotPolars(Data, windSpeed=15, WindTol=15, anglerange=15, minspeed=5):
    Data = polarFilter(Data, anglerange)
    import math
    theta = []
    theta2 = []
    r = []
    for i in Data:
        if i[1]["TWS"] is not None:
            var = abs(i[1]["TWS"] - windSpeed)
            if var < WindTol:
                if i[1]["BSP"] > minspeed:
                    theta.append(math.radians(i[1]["TWA"]))
                    theta2.append(-math.radians(i[1]["TWA"]))
                    r.append(i[1]["BSP"])
    axis = matplotlib.pyplot.subplot(111, projection='polar')
    axis.set_theta_zero_location('N')
    axis.set_theta_direction(-1)
    axis.set_rlabel_position(math.pi/2)
    axis.set_rlim(0, 18)
    axis.plot(theta, r, '.b')
    axis.plot(theta2, r, '.b')
    axis.grid(True)
    axis.set_title("BSP vs TWA (TWS: " + str(windSpeed) + " ± " + str(WindTol) + '  HDG Filter: ± '+str(anglerange) + '  Min Speed =  '+str(minspeed) + ")", va='bottom')
    matplotlib.pyplot.show()

if __name__ == "__main__":
    data = PP_data_import()
    plotPolars(data, windSpeed=10, WindTol=1, anglerange=5, minspeed=6)
    linar_var_plot(data, ['GWD', 'HDG', 'TWA', 'GWS'])
    print('Finito')
