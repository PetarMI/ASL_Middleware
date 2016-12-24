import matplotlib.pyplot as plt
import numpy as np
import csv

folder="/home/petar/AutumnSemester/AdvancedSystems/WriteEffect/Memaslap/tps_logs"
repl_factor="_All"
parsed_file="parsed_memaslap" + repl_factor + "_second.log"

def parse_instance(backends, writes):
    filename1 = folder + "/wr_" + backends + "_" + writes

    i_get_tps = []
    i_get_std = []
    i_get_rt = []
    i_get_perc_high = []
    i_get_perc_low = []
    i_set_tps = []
    i_set_std = []
    i_set_rt = []
    i_set_perc_high = []
    i_set_perc_low = []
    i_tot_tps = []
    i_tot_std = []
    i_tot_rt = []
    i_tot_perc_high = []
    i_tot_perc_low = []


    for server in map(str, range(0, 3)):
        filename2 = filename1 + "_" + server

        r_tps_get = []
        r_std_get = []
        r_rt_get = []
        r_get_perc_high = []
        r_get_perc_low = []
        r_tps_set = []
        r_std_set = []
        r_rt_set = []
        r_set_perc_high = []
        r_set_perc_low = []
        r_tps_tot = []
        r_std_tot = []
        r_rt_tot = []
        r_tot_perc_high = []
        r_tot_perc_low = []

        for repl in map(str, range(0, 3)):
            filename = filename2 + "_" + repl + repl_factor + ".log"
            replica_info = parse_replica(filename)
            r_tps_get.append(replica_info[0][0])
            r_std_get.append(replica_info[0][1])
            r_rt_get.append(replica_info[0][2])
            r_get_perc_high.append(replica_info[0][3])
            r_get_perc_low.append(replica_info[0][4])
            r_tps_set.append(replica_info[1][0])
            r_std_set.append(replica_info[1][1])
            r_rt_set.append(replica_info[1][2])
            r_set_perc_high.append(replica_info[1][3])
            r_set_perc_low.append(replica_info[1][4])
            r_tps_tot.append(replica_info[2][0])
            r_std_tot.append(replica_info[2][1])
            r_rt_tot.append(replica_info[2][2])
            r_tot_perc_high.append(replica_info[2][3])
            r_tot_perc_low.append(replica_info[2][4])  

        i_get_tps.append(np.mean(r_tps_get))
        i_get_std.append(np.mean(r_std_get))
        i_get_rt.append(np.median(r_rt_get))
        i_get_perc_high.append(np.median(r_get_perc_high))
        i_get_perc_low.append(np.median(r_get_perc_low))
        i_set_tps.append(np.mean(r_tps_set))
        i_set_std.append(np.mean(r_std_set))
        i_set_rt.append(np.median(r_rt_set))
        i_set_perc_high.append(np.median(r_set_perc_high))
        i_set_perc_low.append(np.median(r_set_perc_low))
        i_tot_tps.append(np.mean(r_tps_tot))
        i_tot_std.append(np.mean(r_std_tot))
        i_tot_rt.append(np.median(r_rt_tot))
        i_tot_perc_high.append(np.median(r_tot_perc_high))
        i_tot_perc_low.append(np.median(r_tot_perc_low))

    instance_info = []
    instance_info.append((np.sum(i_get_tps), np.mean(i_get_std), np.median(i_get_rt), np.median(i_get_perc_high), np.median(i_get_perc_low)))
    instance_info.append((np.sum(i_set_tps), np.mean(i_set_std), np.median(i_set_rt), np.median(i_set_perc_high), np.median(i_set_perc_low)))
    instance_info.append((np.sum(i_tot_tps), np.mean(i_tot_std), np.median(i_tot_rt), np.median(i_tot_perc_high), np.median(i_tot_perc_low)))

    return instance_info

def parse_replica(file):
    get_tps=[]
    get_rt=[]
    set_tps=[]
    set_rt=[]
    tot_tps=[]
    tot_rt=[]

    f = open(file, 'r')
    text = f.readlines()
    for l in range (10, 110):
        pos = 10 + l*16
        
        # GET info
        period_line = text[pos]
        info = period_line.split()
        get_tps.append(int(info[3]))
        get_rt.append(int(info[8]))

        # SET info
        period_line = text[pos + 5]
        info = period_line.split()
        set_tps.append(int(info[3]))
        set_rt.append(int(info[8]))

        # TOT info
        period_line = text[pos + 10]
        info = period_line.split()
        tot_tps.append(int(info[3]))
        tot_rt.append(int(info[8]))

    all_info = []
    all_info.append((np.mean(get_tps), np.std(get_tps), np.median(get_rt), np.percentile(get_rt, 75), np.percentile(get_rt, 25)))
    all_info.append((np.mean(set_tps), np.std(set_tps), np.median(set_rt), np.percentile(set_rt, 75), np.percentile(set_rt, 25)))
    all_info.append((np.mean(tot_tps), np.std(tot_tps), np.median(tot_rt), np.percentile(tot_rt, 75), np.percentile(tot_rt, 25)))

    return all_info

def parse_backends(backends):
    writes = [1, 5, 10]
    
    backend_results = []

    for wr in map(str, writes):
        instance = parse_instance(str(backends), wr)
        backend_results.append(instance)

    return backend_results

def parse_logs():
    instances = []

    for backends in [3, 5, 7]:
        instances.append(parse_backends(backends))

    write_logs(instances)

def write_logs(instances):
    with open(parsed_file, "w") as file:
        file.write("TPS | TPS_STD | RESP_TIME | 75% | 25%\n")
        for i, backends in zip(range(0, 3), [3, 5, 7]):
            writes = [1, 5, 10]
            for j, wr in zip(range(0, 3), writes): 
                inst = instances[i][j]
                file.write("Backends: " + str(backends) + "|" + "Writes: " + str(wr) + "%\n")
                file.write(",".join(map(str, inst[0])) + "\n")
                file.write(",".join(map(str, inst[1])) + "\n")
                file.write(",".join(map(str, inst[2])) + "\n")
                file.write("\n")

GET = 2
SET = 3
TOT = 4
delta = 4
tps = 0
tps_std = 1
rt = 2
perc_mhigh = 3
perc_mlow = 4
colors = ['green', 'blue', 'red']

mcs = 1000
sec = 1000000

def vis_bars_tps(op_type):
    colors_get = ['forestgreen', 'indigo', 'firebrick']
    colors_set = ['chocolate', 'gold', 'teal']

    vals_tot_none = [[], [], []]
    std_tot_none = [[], [], []]
    vals_tot_all = [[], [], []]
    std_tot_all = [[], [], []]

    with open("parsed_memaslap_None_init.log", "r") as file:
        data = file.readlines()

        for b in range(0, 3):
            for l in range(0, 3): 
                pos = op_type + 5*b + l*15
                info_line = data[pos].split(",")
                val = float(info_line[tps])
                std = float(info_line[tps_std])

                vals_tot_none[b].append(val)
                std_tot_none[b].append(std)

    with open("parsed_memaslap_All_init.log", "r") as file:
        data = file.readlines()

        for b in range(0, 3):
            for l in range(0, 3): 
                pos = op_type + 5*b + l*15
                info_line = data[pos].split(",")
                val = float(info_line[tps])
                std = float(info_line[tps_std])

                vals_tot_all[b].append(val)
                std_tot_all[b].append(std)

    fig, ax = plt.subplots()
    axes = plt.gca()
    axes.set_ylim([0,14550])
    ax.set_xlabel("Backends")
    ax.set_ylabel("Throughput (operations/second)")
    ind = np.arange(3) 
    width = 0.15     
    ax.set_xticks(ind + 3*width)
    ax.set_xticklabels(('3', '5', '7'))

    plots = []

    for j, b in zip(range(0, 3), range(0, 6)[::2]):
        p1 = plt.bar(ind + j*width, vals_tot_none[j], width, color=colors_get[j], yerr=std_tot_none[j], error_kw=dict(capthick=1.5, lw=1.5))
        p2 = plt.bar(ind + j*width + 3*width, vals_tot_all[j], width, color=colors_get[j], yerr=std_tot_all[j], hatch="//", error_kw=dict(capthick=1.5, lw=1.5))
        plots.append(p1)
        plots.append(p2)

    legend1 = plt.legend((plots[0], plots[1]), ("N = 1", "N = All"), loc=3, title="Replication", ncol=2, fancybox=True, prop={'size':11}, fontsize=12)
    plt.legend((plots[0], plots[2], plots[4]), ("1%", "5%", "10%"), loc=4, title="Writes", ncol = 3, fancybox=True, prop={'size':11}, fontsize=12)
    plt.gca().add_artist(legend1)

    plt.show()

def vis_bars_rt(op_type):
    colors_get = ['forestgreen', 'indigo', 'firebrick']
    colors_set = ['chocolate', 'gold', 'teal']

    vals_tot_none = [[], [], []]
    perch_tot_none = [[], [], []]
    percl_tot_none = [[], [], []]
    vals_tot_all = [[], [], []]
    perch_tot_all = [[], [], []]
    percl_tot_all = [[], [], []]

    with open("parsed_memaslap_None_init.log", "r") as file:
        data = file.readlines()

        for b in range(0, 3):
            for l in range(0, 3): 
                pos = op_type + 5*b + l*15
                info_line = data[pos].split(",")
                val = float(info_line[rt])
                perch = float(info_line[perc_mhigh])
                percl = float(info_line[perc_mlow])

                vals_tot_none[b].append(val / mcs)
                perch_tot_none[b].append((perch - val) / mcs)
                percl_tot_none[b].append((val - percl) / mcs)

    with open("parsed_memaslap_All_init.log", "r") as file:
        data = file.readlines()

        for b in range(0, 3):
            for l in range(0, 3): 
                pos = op_type + 5*b + l*15
                info_line = data[pos].split(",")
                val = float(info_line[rt])
                perch = float(info_line[perc_mhigh])
                percl = float(info_line[perc_mlow])

                vals_tot_all[b].append(val / mcs)
                perch_tot_all[b].append((perch - val) / mcs)
                percl_tot_all[b].append((val - percl) / mcs)

    fig, ax = plt.subplots()
    axes = plt.gca()
    axes.set_ylim([0,36])
    ax.set_xlabel("Backends")
    ax.set_ylabel("Response time (ms)")
    ind = np.arange(3) 
    width = 0.15     
    ax.set_xticks(ind + 3*width)
    ax.set_xticklabels(('3', '5', '7'))

    plots = []

    for j, b in zip(range(0, 3), range(0, 6)[::2]):
        p1 = plt.bar(ind + j*width, vals_tot_none[j], width, color=colors_get[j], yerr=np.array([percl_tot_none[j], perch_tot_none[j]]), error_kw=dict(capthick=1.5, lw=1.5))
        p2 = plt.bar(ind + j*width + 3*width, vals_tot_all[j], width, color=colors_get[j], hatch="//", yerr=np.array([percl_tot_all[j], perch_tot_all[j]]), error_kw=dict(capthick=1.5, lw=1.5))
        plots.append(p1)
        plots.append(p2)

    legend1 = plt.legend((plots[0], plots[1]), ("N = 1", "N = All"), loc=3, title="Replication", ncol=2, fancybox=True, prop={'size':12}, fontsize=12)
    plt.legend((plots[0], plots[2], plots[4]), ("1%", "5%", "10%"), loc=4, title="Writes", ncol = 3, fancybox=True, prop={'size':12}, fontsize=12)
    plt.gca().add_artist(legend1)
    
    plt.show()

# vis_bars_tps(TOT)
vis_bars_tps(TOT)
#parse_logs()