import matplotlib.pyplot as plt
import numpy as np
import csv

folder="/home/petar/AutumnSemester/AdvancedSystems/ReplEffect/Memaslap/tps_logs"

def parse_instance(backends, repl):
    filename1 = folder + "/repl_" + backends + "_" + repl

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

        for repl in map(str, range(0, 3)):
            filename = filename2 + "_" + repl + ".log"
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

    instance_info = []
    instance_info.append((np.sum(i_get_tps), np.mean(i_get_std), np.median(i_get_rt), np.median(i_get_perc_high), np.median(i_get_perc_low)))
    instance_info.append((np.sum(i_set_tps), np.mean(i_set_std), np.median(i_set_rt), np.median(i_set_perc_high), np.median(i_set_perc_low)))

    return instance_info

def parse_replica(file):
    get_tps=[]
    get_rt=[]
    set_tps=[]
    set_rt=[]

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

    all_info = []
    all_info.append((np.mean(get_tps), np.std(get_tps), np.median(get_rt), np.percentile(get_rt, 75), np.percentile(get_rt, 25)))
    all_info.append((np.mean(set_tps), np.std(set_tps), np.median(set_rt), np.percentile(set_rt, 75), np.percentile(set_rt, 25)))

    return all_info

def parse_backends(backends):
    middle_repl=backends/2 + 1
    replication=[1, middle_repl, backends]
    
    backend_results = []

    for repl in map(str, replication):
        instance = parse_instance(str(backends), repl)
        backend_results.append(instance)

    return backend_results

def parse_logs():
    instances = []

    for backends in [3, 5, 7]:
        instances.append(parse_backends(backends))

    write_logs(instances)

def write_logs(instances):
    with open("parsed_memaslap.log", "w") as file:
        file.write("TPS | TPS_STD | RESP_TIME | 75% | 25%\n")
        for i, backends in zip(range(0, 3), [3, 5, 7]):
            replication = [1, backends/2 + 1, backends]
            for j, repl in zip(range(0, 3), replication): 
                inst = instances[i][j]
                file.write("Backends: " + str(backends) + "|" + "Repl_factor: " + str(repl) + "\n")
                file.write(",".join(map(str, inst[0])) + "\n")
                file.write(",".join(map(str, inst[1])) + "\n")
                file.write("\n")

GET = 2
SET = 3
delta = 4
tps = 0
tps_std = 1
rt = 2
perc_mhigh = 3
perc_mlow = 4
colors = ['green', 'blue', 'red']

mcs = 1000
sec = 1000000

def vis_logs(op_type, metric):
    values = [[], [], []]

    with open("parsed_memaslap.log", "r") as file:
        data = file.readlines()

        for b in range(0, 3):
            for l in range(0, 3): 
                pos = op_type + 3*b*delta + l*delta
                val = data[pos].split(",")[metric]
                values[b].append(val)

    repl_axis = [[1, 2, 3], [1, 3, 5], [1, 4, 7]]

    fig, ax = plt.subplots()
    axes = plt.gca()
    axes.set_xlim([0.5,7.5])
    ax.set_xlabel("Replication factor")
    ax.set_ylabel("Response time ()")

    for j, b in zip(range(0, 3), [3, 5, 7]):
        ax.plot(repl_axis[j], values[j], '-o', label="Backends = {0}".format(b))

    # plt.legend(loc=1, ncol=2, prop={'size':10}, shadow=True, title="Legend", fancybox=True, fontsize=12)
    # ax.get_legend().get_title().set_color("black")

    plt.show()

def vis_logs_tps():
    vals_get = [[], [], []]
    std_get = [[], [], []]

    vals_set = [[], [], []]
    std_set = [[], [], []]

    with open("parsed_memaslap.log", "r") as file:
        data = file.readlines()

        for b in range(0, 3):
            for l in range(0, 3): 
                pos = GET + 3*b*delta + l*delta
                info_line = data[pos].split(",")
                val = float(info_line[tps])
                std = float(info_line[tps_std])

                vals_get[b].append(val)
                std_get[b].append(std)

        for b in range(0, 3):
            for l in range(0, 3): 
                pos = SET + 3*b*delta + l*delta
                info_line = data[pos].split(",")
                val = float(info_line[tps])
                std = float(info_line[tps_std])

                vals_set[b].append(val)
                std_set[b].append(std)

    repl_axis = [[1, 2, 3], [1, 3, 5], [1, 4, 7]]

    fig, ax = plt.subplots()
    axes = plt.gca()
    axes.set_xlim([0.5,7.5])
    ax.set_xlabel("Replication factor")
    ax.set_ylabel("Throughput (ops/sec)")

    for j, b in zip(range(0, 3), [3, 5, 7]):
        plt.errorbar(repl_axis[j], vals_get[j], std_get[j], marker='o', color=colors[j], label="GET Backends = {0}".format(b))
        plt.errorbar(repl_axis[j], vals_set[j], std_set[j], marker='^', color=colors[j], label="SET Backends = {0}".format(b))
        

    plt.legend(loc=4, ncol=2, prop={'size':8}, shadow=True, title="Legend", fancybox=True, fontsize=12)
    ax.get_legend().get_title().set_color("black")

    plt.show()

def vis_logs_perc(op_type):
    values = [[], [], []]
    percsh = [[], [], []]
    percsl = [[], [], []]

    with open("parsed_memaslap.log", "r") as file:
        data = file.readlines()

        for b in range(0, 3):
            for l in range(0, 3): 
                pos = op_type + 3*b*delta + l*delta
                info_line = data[pos].split(",")
                val = info_line[rt]
                perch = info_line[perc_mhigh]
                percl = info_line[perc_mlow]

                values[b].append(float(val) / mcs)
                percsh[b].append(float(perch) / mcs)
                percsl[b].append(float(percl) / mcs)

    repl_axis = [[1, 2, 3], [1, 3, 5], [1, 4, 7]]

    fig, ax = plt.subplots()
    axes = plt.gca()
    axes.set_xlim([0.5,8.0])
    ax.set_xlabel("Replication factor")
    ax.set_ylabel("Response time (ms)")

    for j, b in zip(range(0, 3), [3, 5, 7]):
        ax.plot(repl_axis[j], values[j], marker='o', color=colors[j], label="Backends = {0}".format(b))
        ax.plot(repl_axis[j], percsh[j], marker='^', linestyle='--', color=colors[j], label="75th Percentile Backends = {0}".format(b))
        ax.plot(repl_axis[j], percsl[j], marker='^', linestyle='--', color=colors[j], label="25th Percentile Backends = {0}".format(b))

    plt.legend(loc=4, ncol=1, prop={'size':10}, shadow=True, title="Legend", fancybox=True, fontsize=12)
    ax.get_legend().get_title().set_color("black")

    plt.show()

def vis_bars_rt():
    colors_get = ['forestgreen', 'indigo', 'firebrick']
    colors_set = ['chocolate', 'gold', 'teal']

    vals_get = [[], [], []]
    percsh_get = [[], [], []]
    percsl_get = [[], [], []]

    vals_set = [[], [], []]
    percsh_set = [[], [], []]
    percsl_set = [[], [], []]

    with open("parsed_memaslap.log", "r") as file:
        data = file.readlines()

        for b in range(0, 3):
            for l in range(0, 3): 
                pos = SET + 4*b + l*12
                info_line = data[pos].split(",")
                val = float(info_line[rt])
                perch = float(info_line[perc_mhigh])
                percl = float(info_line[perc_mlow])

                vals_get[b].append(val / sec)
                percsh_get[b].append((perch - val) / sec)
                percsl_get[b].append((val - percl) / sec)

        for b in range(0, 3):
            for l in range(0, 3): 
                pos = SET + 4*b + l*delta
                info_line = data[pos].split(",")
                val = float(info_line[rt])
                perch = float(info_line[perc_mhigh])
                percl = float(info_line[perc_mlow])

                vals_set[b].append(val / sec)
                percsh_set[b].append((perch - val) / sec)
                percsl_set[b].append((val - percl) / sec)


    fig, ax = plt.subplots()
    ind = np.arange(3) 
    width = 0.2     
    ax.set_xticks(ind + 1.5*width)
    ax.set_xticklabels(('3', '5', '7'))

    for j, b in zip(range(0, 3), [3, 5, 7]):
        plt.bar(ind + j*width, vals_get[j], width, color=colors_get[j], yerr=np.array([percsl_get[j], percsh_get[j]]))
        plt.bar(ind + j*width, vals_set[j], width, color=colors_set[j], yerr=np.array([percsl_set[j], percsh_set[j]]))

    plt.show()

# vis_logs_tps()
vis_logs_perc(SET)
# vis_bars_rt()
# parse_logs()