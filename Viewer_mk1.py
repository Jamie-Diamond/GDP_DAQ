
def viewer1():
    from Data_import import PP_data_import, data_time_trim
    from Plotting_ToolBox import GPS_plot, linar_var_plot
    import matplotlib.pyplot

    # Get data

    data = PP_data_import()

    #Find times

    fin = len(data)-1
    freq = 10/(data[100][0] - data[90][0])
    idx = 500
    leng = 180
    samples = int(freq * leng-1)
    N, E, A = [0], [0], [0]
    cog, cogt, cow, cowt = [0], [0], [0], [0]
    hdg, hdgt, sog, sogt = [0], [0], [0], [0]
    bsp, bspt = [], []
    while idx < fin-samples:
        idxS = idx
        idxF = idx+samples
        T1 = data[idxS][0]
        T2 = data[idxF][0]
        N, E, A = GPS_slim_data_retrive(data, idxS, idxF, N, E, A)
        slimline_GPS_plot(N, E, A, pause=0.0000001, fig=124)
        slim_data_retrive(data, idxS, idxF, cog, cogt, 'COG')
        slim_data_retrive(data, idxS, idxF, hdg, hdgt, 'HDG')
        slim_data_retrive(data, idxS, idxF, cow, cowt, 'COW')
        slim_data_retrive(data, idxS, idxF, sog, sogt, 'SOG')
        slim_data_retrive(data, idxS, idxF, bsp, bspt, 'BSP')
        slimline_linar_var_plot([cog, cow, hdg], [cogt, cowt, hdgt], ['COG', 'COW', 'HDG'], pause=0.0000001)
        slimline_linar_var_plot([sog, bsp], [sogt, bspt], ['SOG', 'BSP'], pause=0.0000001, fig=1)
        idx += 4




    # # good upwind segment here
    # data = data_time_trim(data, 1479042400, 1479043500)
    # linar_var_plot(data, ['GWD', 'COG', 'TWA', 'TWD'])
    # from polarPlotTools import plotPolars
    # plotPolars(data, bodge=30)
    # GPS_plot(data)
    # import matplotlib.pyplot
    # matplotlib.pyplot.show()


def slim_data_retrive(data, idx_s, idx_f, mag, time, key):
    import time as t
    import datetime

    idx = idx_s
    length = idx_f - idx_s
    while idx < idx_f:
        mag.append(data[idx][1][key])
        #time.append(data[idx][0])
        time.append(datetime.datetime.strptime(t.strftime('%H:%M:%S', t.localtime(data[idx][0])),'%H:%M:%S'))
        if len(mag) > length:
            mag.pop(0)
            time.pop(0)
        idx += 1
    return mag, time



def slimline_linar_var_plot(mag, times, key, pause=False, fig=111, xlim=None):
    import matplotlib.pyplot as plt
    import matplotlib

    plt.figure(fig)
    plt.gcf().clear()
    idx = 0
    for i in key:
        var = mag[idx]
        #time = times[idx]
        time = matplotlib.dates.date2num(times[idx])
        plt.plot_date(time, var, 'o', label=i)
        plt.gca().xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M:%S'))
        if xlim is not None:
            plt.xlim(xlim)
        plt.legend()
        idx += 1
    if type(pause) is float:
        plt.pause(pause)


def GPS_slim_data_retrive(data, idx_s, idx_f, N, E, A):
    idx = idx_s
    length = idx_f - idx_s
    while idx < idx_f:
        N.append(data[idx][1]['Northing'])
        E.append(data[idx][1]['Easting'])
        A.append(data[idx][1]['Accuracy']/2)
        if len(N) > length:
            N.pop(0)
            E.pop(0)
            A.pop(0)
        idx += 1
    return N, E, A

def slimline_GPS_plot(N, E, A, pause=False, fig=123):
    '''Plots GPS data'''
    import matplotlib.pyplot as plt
    plt.figure(fig)
    plt.gcf().clear()
    plt.errorbar(E, N, xerr=A, yerr=A, label='GPS', ecolor='b', color='k', marker='o')
    plt.legend()
    plt.xlabel("East [m]")
    plt.ylabel("North [m]")
    plt.grid(True)
    plt.axis('equal')
    if type(pause) is float:
        plt.pause(pause)


viewer1()