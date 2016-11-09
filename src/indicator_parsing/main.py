from os.path import exists, join

ind_name = [
    "DailyActiveTimeRatio",
    "DailyEntropy",
    "DailyHouseEntropy",
    "TotalDailySleep",
    "TotalDailyWater"
]

plot_yAxis = [
    "Activity Daily Time [h]",
    "Entropy",
    "Entropy",
    "Activation Time [h]",
    "Water Consumption [l]"
]


def parse_data():
    from outlier_detector import OutlierDetector
    import matplotlib.pyplot as plt
    path = "/home/fabio/data/indicators"
    drift = False
    num_ind = 0
    indicators = {}
    for ind in ind_name:
        if num_ind in (3,):
            div = 1.0 / 3600
        elif num_ind in (0,):
            div = 24
        else:
            div = 1
        indicators[num_ind] = {}
        days = 0
        lastchunk = ""
        for x in range(2):
            fpath = join(path, ind)
            if drift:
                fpath += "WithDrift"
                drift = False
            else:
                fpath += "NoDrift"
                drift = True
            fpath += ".txt"

            if not exists(fpath):
                break
            else:
                print(fpath)
            input_file = open(fpath)
            for line in input_file:
                chunks = line.split(" ")
                indicators[num_ind][days] = \
                    float(chunks[3]) * div
                if lastchunk != chunks[6]:
                    days += 1
                lastchunk = chunks[6]
        num_ind += 1
    # for ind
    print("debug")
    results = {}
    plt.ion()
    for j in range(len(indicators)):
        ind = indicators[j]
        results[j] = {}
        print("\n" + "Indicator " + ind_name[j])
        dect = OutlierDetector(outlier_conf=0.9, window_length=28)
        print(len(ind))
        for i in ind:
            res = dect.parse(ind[i])
            if res[0]:
                print("Day " + str(i + 1) + " was detected as outlier")
                results[j][i] = "outlier"
            elif res[1]:
                print("Day " + str(i + 1) + " was detected as warning")
                results[j][i] = "warning"
        print("...done")
        plt.figure()
        plt.step(list(ind.keys())[:91], list(ind.values())[:91], where='mid')
        plt.step(list(ind.keys())[90:], list(ind.values())[90:], 'r', where='mid')

        for r in results[j]:
            if results[j][r] == "warning":
                plt.plot(r, list(ind.values())[r], 'ko', color="white")
            elif results[j][r] == "outlier":
                plt.plot(r, list(ind.values())[r], 'ko')
        plt.xlabel("Time [days]")
        plt.ylabel(plot_yAxis[j])
        if plot_yAxis[j] == "Entropy":
            plt.legend(["Routine", "Drift"], loc=3)
        else:
            plt.legend(["Routine", "Drift"], loc=2)

    plt.ioff()
    plt.show()


if __name__ == "__main__":
    parse_data()
