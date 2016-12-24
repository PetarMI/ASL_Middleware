def get_repl_data():
    tpss = []
    rts = []

    with open("/home/petar/AutumnSemester/AdvancedSystems/Milestone3/InteractiveLaw/repl_parsed_memaslap.log", "r") as file:
        data = file.readlines()

        for i in range(0, 9): 
            pos = 2 + 4*i
            info_line = data[pos].split(",")

            tps = float(info_line[0])
            grt = float(info_line[2])
            
            info_line = data[pos + 1].split(",")
            tps += float(info_line[0])
            srt = float(info_line[2])

            tpss.append(tps)
            rts.append(micros_to_sec(0.99 * grt + 0.01 * srt))

    return tpss, rts

def get_wr_data():
    tps = []
    rts = []

    with open("/home/petar/AutumnSemester/AdvancedSystems/Milestone3/InteractiveLaw/write_parsed_memaslap_All.log", "r") as file:
        data = file.readlines()

        for i in range(0, 9): 
            pos = 4 + 5*i
            info_line = data[pos].split(",")
            tps.append(float(info_line[0]))
            rts.append(micros_to_sec(float(info_line[2])))

    return tps, rts

def micros_to_sec(micros):
    return micros / 1000000

def get_Z(X, R):
    Zs = []

    N = 360
    for rt, tps in zip(R, X):
        tt = N / tps - rt
        Zs.append(tt)

    return Zs

def main():
    tpss, rts = get_wr_data()
    print "Metrics"
    print_metrics(tpss, rts)

    think_times = get_Z(tpss, rts)
    print "Think times"
    print_times(think_times)

def print_metrics(a, b):
    for g, s in zip(a, b):
        print str(g) + " " + str(s)

    print ""

def print_times(ts):
    for t in ts:
        print t

    print ""

main()


