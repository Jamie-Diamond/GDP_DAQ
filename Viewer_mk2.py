import matplotlib.pyplot as plt


def viewer2():
    from Data_import import PP_data_import
    # Get data
    data = PP_data_import()
    twa, cow, cog, hdg, sog, bsp, E, N, T, A = data_prep(data)
    fin = len(data)-1
    freq = 10/(data[100][0] - data[90][0])
    idx = 500
    leng = 100
    delta = 2
    samples = int(freq * leng-1)
    thisfig = plt.figure(1)
    while idx < fin-samples:
        idxS = idx
        idxF = idx+samples
        slimline_GPS_plot(N, E, N[idxS:idxF], E[idxS:idxF], A[idxS:idxF], thisfig, subfig=1)
        slimline_linar_var_plot([cog[idxS:idxF], cow[idxS:idxF], hdg[idxS:idxF]], T[idxS:idxF], ['COG', 'COW', 'HDG'], thisfig, subfig=2)
        slimline_linar_var_plot([sog[idxS:idxF], bsp[idxS:idxF]], T[idxS:idxF], ['SOG', 'BSP'], thisfig, subfig=3)
        polar(twa[idxS:idxF], bsp[idxS:idxF], thisfig)
        plt.pause(0.00000001)
        idx += delta

def data_prep(data):
    twa, cow, cog, hdg, sog, bsp, E, N, T, Acc = [], [], [], [], [], [], [], [], [], []
    for i in data:
        cog.append(i[1]['COG'])
        hdg.append(i[1]['HDG'])
        sog.append(i[1]['SOG'])
        bsp.append(i[1]['BSP'])
        cow.append(i[1]['COW'])
        twa.append(i[1]['COW'])
        E.append(i[1]['Easting'])
        N.append(i[1]['Northing'])
        T.append(i[0])
        Acc.append(i[1]['Accuracy'])
    return twa, cow, cog, hdg, sog, bsp, E, N, T, Acc


def slimline_linar_var_plot(dat, time, key, thisfig, subfig=1):
    ax = thisfig.add_subplot(2,2,subfig)
    ax.clear()
    idx = 0
    for i in key:
        var = dat[idx]
        ax.plot(time, var, '-', label=i)
        ax.legend()
        idx += 1
    ax.set_xlim([time[0], time[-1]])


def slimline_GPS_plot(n1, e1, N, E, A, thisfig,subfig=1):
    '''Plots GPS data'''
    ax = thisfig.add_subplot(2, 2, subfig)
    ax.clear()
    ax.errorbar(E, N, xerr=A, yerr=A, ecolor='b', color='k', marker='o')
    ax.scatter(E[-1], N[-1], marker='D', color='r', s=500)
    ax.plot(e1, n1, '-')
    ax.grid(True)
    ax.axis('equal')

def polar(Wind, Speed, thisfig,subfig=4):
    import math
    axis = thisfig.add_subplot(2,2,subfig, projection='polar')
    axis.clear()
    axis.set_theta_zero_location('N')
    axis.set_theta_direction(-1)
    axis.set_rlabel_position(math.pi / 2)
    theta = []
    for i in Wind:
        theta.append(math.radians(i))
    axis.set_rlim(0, 18)
    axis.plot(theta, Speed, '.b')
    axis.plot(theta[-1], Speed[-1], 'rD', markersize=10)
    axis.grid(True)

if __name__ == "__main__":
    viewer2()