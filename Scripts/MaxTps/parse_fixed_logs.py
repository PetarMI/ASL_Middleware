import matplotlib.pyplot as plt
import numpy as np

folder="/home/petar/AutumnSemester/AdvancedSystems/MaxTpsLogs/Memaslap/Fixed_Threads/final_fixed"

def parse_instance(clients, r):
    filename1 = folder + "/max_tps_" + clients + "_32"

    instance_tps=[]
    instance_std=[]

    for server in map(str, range(0, 5)):
        filename2 = filename1 + "_" + server

        repl_tps=[]
        repl_std=[]

        for repl in map(str, range(0, r)):
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
    print file
    text = f.readlines()
    for l in range (4, 49):
        period_line = text[10 + l*11]
        info = period_line.split()
        tps.append(int(info[3]))

    mean = np.mean(tps)
    std = np.std(tps)

    return mean, std

def parse_logs():
    tps_instances=[]
    std_instances=[]

    for clients in map(str, range(20, 160)[::20]):
        tps, std = parse_instance(clients, 3)
        tps_instances.append(tps)
        std_instances.append(std)

    # tps, std = parse_instance("140", 1)
    # tps_instances.append(tps)
    # std_instances.append(std)

    vis_logs(tps_instances, std_instances)

def vis_logs(tpss, stds):
    print tpss[3]
    print stds[3]

    fig, ax = plt.subplots()
    axes = plt.gca()
    axes.set_xlim([80,720])
    ax.set_xlabel("Virtual clients")
    ax.set_ylabel("TPS (Gets/second)")
    plt.errorbar((range(100, 800)[::100]), tpss, stds, linestyle='-', marker='o')

    plt.show()

parse_logs()