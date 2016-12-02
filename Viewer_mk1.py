
def viewer1():
    from Data_import import PP_data_import, data_time_trim
    from Plotting_ToolBox import GPS_plot, linar_var_plot
    import matplotlib.pyplot

    # Get data

    data = PP_data_import()
    #Find times

    fin = len(data)-1
    freq = 10/(data[100][0] - data[90][0])
    idx = 0
    leng = 180
    samples = int(freq * leng-1)
    while idx < fin-samples:

        idxS = idx
        idxF = idx+samples
        T1 = data[idxS][0]
        T2 = data[idxF][0]
        data_trim = data_time_trim(data, T1, T2)
        GPS_plot(data_trim, pause=0.00000000001)
        linar_var_plot(data_trim,['SOG', 'BSP', 'TDS', 'AWS'], pause=0.000000000001, fig=8)
        linar_var_plot(data_trim, ['COG', 'HDG', 'COW'], pause=0.0000000000001, fig=9)
        idx += 500
    #
    # from Plotting_ToolBox import linar_var_plot, GPS_plot
    # # good upwind segment here
    # data = data_time_trim(data, 1479042400, 1479043500)
    # linar_var_plot(data, ['GWD', 'COG', 'TWA', 'TWD'])
    # from polarPlotTools import plotPolars
    # plotPolars(data, bodge=30)
    # GPS_plot(data)
    # import matplotlib.pyplot
    # matplotlib.pyplot.show()