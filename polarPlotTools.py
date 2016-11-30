from Data_import import PP_data_import
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


def plotPolars(Data, windSpeed=15, error=15):
    import math
    theta = []
    r = []
    for i in Data:
        if i[1]["GWS"] is not None:
            var = abs(i[1]["GWS"] - windSpeed)
            if var < error:
                theta.append(math.radians(i[1]["TWA"]))
                r.append(i[1]["SOG"])
    print(theta)
    print(max(theta))
    print(min(theta))
    axis = matplotlib.pyplot.subplot(111, projection='polar')
    axis.set_theta_zero_location('N')
    axis.set_theta_direction(-1)
    axis.set_rlabel_position(math.pi/2)
    axis.plot(theta, r, '+b')
    axis.grid(True)
    axis.set_title("Boat Speed vs Wind Direction (Wind Speed: " + str(windSpeed) + "±" + str(error) + ")", va='bottom')
    matplotlib.pyplot.show()


data = PP_data_import(reprocess=False)
plotPolars(polarFilter(data, 5), 13, 10)
linar_var_plot(data,['TWA'])