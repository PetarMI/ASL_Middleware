import matplotlib.pyplot as plt
import numpy as np
import csv

folder="/home/petar/AutumnSemester/AdvancedSystems/MaxTpsLogs/Memaslap/Var_Threads_2k/tps_logs"

def parse_instance(clients, threads):
    filename1 = folder + "/max_tps_" + clients + "_" + threads

    instance_tps=[]
    instance_std=[]

    for server in map(str, range(0, 5)):
        filename2 = filename1 + "_" + server

        repl_tps=[]
        repl_std=[]

        for repl in map(str, range(0, 2)):
           filename = filename2 + "_" + repl + ".log"
           mean, std = parse_repl(filename)
           repl_tps.append(mean)
           repl_std.append(std)

        instance_tps.append(np.mean(repl_tps))
        instance_std.append(np.mean(repl_std))

    mean_tps = np.sum(instance_tps)
    mean_std = np.mean(instance_std)

    return mean_tps, mean_std

def parse_repl(file):
    tps=[]
    f = open(file, 'r')
    text = f.readlines()
    for l in range (4, 49):
        period_line = text[10 + l*11]
        info = period_line.split()
        tps.append(int(info[3]))

    mean = np.mean(tps)
    std = np.std(tps)

    return mean, std

def parse_threads(threads):
    tps_instances=[]
    std_instances=[]

    for clients in map(str, range(72, 92)[::4]):
        tps, std = parse_instance(clients, threads)
        tps_instances.append(tps)
        std_instances.append(std)

    # tps, std = parse_instance("88", threads)
    # tps_instances.append(tps)
    # std_instances.append(std)

    return tps_instances, std_instances

def parse_logs():
    tps_results=[]
    std_results=[]

    for threads in map(str, [8, 16, 32, 64, 128]):
        tps, std = parse_threads(threads)
        tps_results.append(tps)
        std_results.append(std)

    # write_logs(tps_results, std_results)

def write_logs(tpss, stds):
    with open("parsed_var_threads_repl.log", "w") as file:
        file.write(",".join(map(str, range(360, 460)[::20])) + "\n")
        for t in range(0, 5): 
            file.write(",".join(map(str, map(int, tpss[t]))) + "\n")
        file.write("\n")
        for t in range(0, 5): 
            file.write(",".join(map(str, map(int, stds[t]))) + "\n")

def vis_all_logs():
    tps=[[], [], [], [], []]
    with open("parsed_mem_final.log", "r") as file:
        data = file.readlines()
        t = 0
        for l in range(1, 6):
            split_line = data[l].split(",")
            for i in range(0, 5):
                tps[t].append(split_line[i])
            t += 1

    print tps

    fig, ax = plt.subplots()
    axes = plt.gca()
    axes.set_xlim([355,445])
    ax.set_xlabel("Virtual client")
    ax.set_ylabel("TPS (Gets/second)")

    j = 0
    for i in [8, 16, 32, 64, 128]:
        ax.plot((range(360, 460)[::20]), tps[j], '-o', label="Threads = {0}".format(i))
        j += 1

    plt.legend(loc=1, ncol=2, prop={'size':10}, shadow=True, title="Legend", fancybox=True, fontsize=12)
    ax.get_legend().get_title().set_color("black")

    plt.show()

def vis_best_std():
    tps=[[], []]
    std = [[], []]
    
    with open("parsed_mem_final.log", "r") as file:
        t = 0
        data = file.readlines()

        for l in range(1, 3):
            split_line = data[l].split(",")
            for i in range(0, 5):
                tps[t].append(int(split_line[i]))
            t += 1

        t = 0 
        for l in range(6, 8):
            split_line = data[l].split(",")
            for i in range(0, 5):
                std[t].append(int(split_line[i]))
            t += 1 

    fig, ax = plt.subplots()
    axes = plt.gca()
    axes.set_xlim([375,465])
    ax.set_xlabel("Virtual client")
    ax.set_ylabel("TPS (Gets/second)")

    for arr in tps:
        print arr

    for arr in std:
        print arr

    plt.errorbar(range(380, 480)[::20], tps[0], std[0], label="8 threads", linestyle='-', marker='o', color='r', ecolor='r')
    plt.errorbar(range(380, 480)[::20], tps[1], std[1], label="16 threads", linestyle='-', marker='o', color='b', ecolor='b')
    
    plt.legend(loc="upper left", bbox_to_anchor=[0, 1], ncol=2, shadow=True, title="Legend", fancybox=True, fontsize=12)

    plt.show()

# vis_all_logs()
vis_best_std()
# parse_logs()

# def kiro():
#     fig, ax = plt.subplots()
#     axes = plt.gca()
#     axes.set_xlim([0.8,2.2])
#     axes.set_ylim([0, 16])
#     ax.set_xlabel("Log")
#     ax.set_ylabel("Response time (ms)")

#     # plt.rc('axes', prop_cycle=(cycler('color', ['r', 'b'])

#     plt.errorbar(range(1, 2)[::1], [0.58791660487], [5.8068705363], label="400 quick network", linestyle='None', marker='o')
#     plt.errorbar(range(2, 3)[::1], [1.54306562724], [13.1751770232], label="400 slow network", linestyle='None', marker='o')

#     plt.legend(loc="upper left", bbox_to_anchor=[0, 1], ncol=2, shadow=True, title="Legend", fancybox=True, fontsize=12)
#     plt.show()

# kiro()