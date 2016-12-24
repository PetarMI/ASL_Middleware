import argparse
import matplotlib.pyplot as plt
import numpy as np
import csv
import operator

folder="/home/petar/AutumnSemester/AdvancedSystems/WriteEffect/Timestamps/MaxTps"
REPLICATION = "None"

ms=1000000
s = 1000

def parse_instance(backends, repl):
    filename1 = folder + "/RequestLog_" + backends + "_" + repl

    get_parse_time = []
    get_queue_time = []
    get_server_time = []
    get_return_time = []
    get_total_time = []
    set_parse_time = []
    set_queue_time = []
    set_process_time = []
    set_server_time = []
    set_return_time = []
    set_total_time = []

    for r in map(str, range(0, 3)):
        filename = filename1 + "_" + r + "_" + REPLICATION + ".log"
        
        with open (filename, 'r') as csvlog:
            for line in csvlog:
                split_line = line.split(",")
                if len(split_line) <= 3:
                    continue
                parset=(float(split_line[1]) / ms)
                queuet=(float(split_line[2]) / ms)
                proct=(float(split_line[3]) / ms)
                servert=(float(split_line[4]) / ms)
                returnt=(float(split_line[5]) / ms)
                totalt=(float(split_line[6]) / ms)
                if (split_line[0]=="get"):
                    get_parse_time.append(parset)
                    get_queue_time.append(queuet)
                    get_server_time.append(servert)
                    get_return_time.append(returnt)
                    get_total_time.append(totalt)
                elif (split_line[0]=="set"):
                    set_parse_time.append(parset)
                    set_queue_time.append(queuet)
                    set_process_time.append(proct)
                    set_server_time.append(servert)
                    set_return_time.append(returnt)
                    set_total_time.append(totalt)
                else:
                    print("hhs")

    all_info = []
    all_info.append((np.mean(get_parse_time), np.median(get_parse_time), np.percentile(get_parse_time, 75), np.percentile(get_parse_time, 25)))
    all_info.append((np.mean(get_queue_time), np.median(get_queue_time), np.percentile(get_queue_time, 75), np.percentile(get_queue_time, 25)))
    all_info.append((np.mean(get_server_time), np.median(get_server_time), np.percentile(get_server_time, 75), np.percentile(get_server_time, 25)))
    all_info.append((np.mean(get_return_time), np.median(get_return_time), np.percentile(get_return_time, 75), np.percentile(get_return_time, 25)))
    all_info.append((np.mean(get_total_time), np.median(get_total_time), np.percentile(get_total_time, 75), np.percentile(get_total_time, 25)))
    all_info.append((np.mean(set_parse_time), np.median(set_parse_time), np.percentile(set_parse_time, 75), np.percentile(set_parse_time, 25)))
    all_info.append((np.mean(set_queue_time), np.median(set_queue_time), np.percentile(set_queue_time, 75), np.percentile(set_queue_time, 25)))
    all_info.append((np.mean(set_server_time), np.median(set_server_time), np.percentile(set_server_time, 75), np.percentile(set_server_time, 25)))
    all_info.append((np.mean(set_return_time), np.median(set_return_time), np.percentile(set_return_time, 75), np.percentile(set_return_time, 25)))
    all_info.append((np.mean(set_total_time), np.median(set_total_time), np.percentile(set_total_time, 75), np.percentile(set_total_time, 25)))

    return all_info

def parse_repl_factor(backends):
    writes = [1, 5, 10]
    repl_factors_results = []

    for wr in map(str, writes):
        instance = parse_instance(str(backends), wr)
        repl_factors_results.append(instance)

    return repl_factors_results

def parse_logs():
    instances = []
    
    for backends in [3, 5, 7]:
        instances.append(parse_repl_factor(backends))

    write_logs(instances)

def write_logs(instances):
    with open("parsed_timestamps_None_second.log", "w") as file:
        file.write("Mean | Median | Percentile (75) | Percentile (25)\n")
        for i, backends in zip(range(0, 3), [3, 5, 7]):
            writes = [1, 5, 10]
            for j, wr in zip(range(0, 3), writes): 
                inst = instances[i][j]
                file.write("Backends: " + str(backends) + "|" + "Writes: " + str(wr) + "%\n")
                file.write("GETs\n")
                for k in range(0, 5):
                    file.write(",".join(map(str, inst[k])) + "\n")
                file.write("SETs\n")
                for k in range(5, 10):
                    file.write(",".join(map(str, inst[k])) + "\n")
                file.write("\n")

GET = 2
SET = 8
parset = 1
queuet = 2
servert = 3
returnt = 4
totalt = 5
delta = 14
mean = 0
median = 1
perc_mhigh = 2
perc_mlow = 3

colors = ['green', 'blue', 'red']

def vis_logs(op_type, t, metric):
    values = [[], [], []]

    with open("parsed_timestamps.log", "r") as file:
        data = file.readlines()

        for b in range(0, 3):
            for l in range(0, 3): 
                pos = op_type + 3*b*delta + l*delta + t
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

    plt.legend(loc=1, ncol=2, prop={'size':10}, shadow=True, title="Legend", fancybox=True, fontsize=12)
    ax.get_legend().get_title().set_color("black")

    plt.show()

def vis_logs_err(op_type, t):
    values = [[], [], []]
    err_high = [[], [], []]
    err_low = [[], [], []]

    with open("parsed_timestamps.log", "r") as file:
        data = file.readlines()

        for b in range(0, 3):
            for l in range(0, 3): 
                pos = op_type + 3*b*delta + l*delta + t
                val = float(data[pos].split(",")[median])
                perc_high = float(data[pos].split(",")[perc_mhigh])
                perc_low = float(data[pos].split(",")[perc_mlow])
                values[b].append(val)
                err_high[b].append(perc_high)
                err_low[b].append(val)

    repl_axis = [[1, 2, 3], [1, 3, 5], [1, 4, 7]]

    fig, ax = plt.subplots()
    axes = plt.gca()
    axes.set_xlim([0.5,7.5])
    ax.set_xlabel("Replication factor")
    ax.set_ylabel("Response time (seconds)")

    # print np.array([err_high[0], err_low[0]])

    for j, b in zip(range(0, 3), [3, 5, 7]):
        ax.plot(repl_axis[j], values[j], '-o', color=colors[j], label="Backends = {0}".format(b))
        ax.plot(repl_axis[j], err_high[j], '-^', linestyle='--', color=colors[j], label="75th Perc Backends = {0}".format(b))
        ax.plot(repl_axis[j], err_low[j], '-^', linestyle='--', color=colors[j], label="25th Perc Backends = {0}".format(b))

    plt.legend(loc=1, ncol=1, prop={'size':9}, shadow=True, title="Legend", fancybox=True, fontsize=10)
    ax.get_legend().get_title().set_color("black")

    plt.show()

def vis_logs_perc(op_type, t):
    values = [[], [], []]
    err_high = [[], [], []]

    with open("parsed_timestamps.log", "r") as file:
        data = file.readlines()

        for b in range(0, 3):
            for l in range(0, 3): 
                pos = op_type + 3*b*delta + l*delta + t
                info_line = data[pos].split(",")
                val = float(info_line[median])
                perc_high = float(info_line[perc_mhigh])
                values[b].append(val)
                err_high[b].append(perc_high)

    repl_axis = [[1, 2, 3], [1, 3, 5], [1, 4, 7]]

    fig, ax = plt.subplots()
    axes = plt.gca()
    axes.set_xlim([0.5,7.5])
    ax.set_xlabel("Replication factor")
    ax.set_ylabel("Response time ()")

    for j, b in zip(range(0, 3), [3, 5, 7]):
        ax.plot(repl_axis[j], values[j], '-o', color=colors[j], label="Backends = {0}".format(b))
        ax.plot(repl_axis[j], err_high[j], '-^', color=colors[j], label="75th Percentile Backends = {0}".format(b))

    # plt.legend(loc=1, ncol=2, prop={'size':8}, shadow=True, title="Legend", fancybox=True, fontsize=12)
    # ax.get_legend().get_title().set_color("black")

    plt.show()

def vis_bars_rt(t):
    colors_get = ['forestgreen', 'indigo', 'firebrick']
    colors_set = ['chocolate', 'gold', 'teal']

    vals_none = [[], [], []]
    percsh_none = [[], [], []]
    percsl_none = [[], [], []]

    vals_all = [[], [], []]
    percsh_all = [[], [], []]
    percsl_all = [[], [], []]

    with open("parsed_timestamps_None.log", "r") as file:
        data = file.readlines()

        for b in range(0, 3):
            for l in range(0, 3): 
                pos = SET + b*14 + l*42 + t
                info_line = data[pos].split(",")
                val = float(info_line[median])
                perch = float(info_line[perc_mhigh])
                percl = float(info_line[perc_mlow])

                vals_none[b].append(val)
                percsh_none[b].append((perch - val))
                percsl_none[b].append((val - percl))
        
    with open("parsed_timestamps_All.log", "r") as file:
        data = file.readlines()

        for b in range(0, 3):
            for l in range(0, 3): 
                pos = SET + b*14 + l*42 + t
                info_line = data[pos].split(",")
                val = float(info_line[median])
                perch = float(info_line[perc_mhigh])
                percl = float(info_line[perc_mlow])

                vals_all[b].append(val)
                percsh_all[b].append((perch - val))
                percsl_all[b].append((val - percl))


    fig, ax = plt.subplots()
    ind = np.arange(3) 
    width = 0.15   
    # axes = plt.gca()
    # axes.set_ylim([0, 0.35])
    ax.set_ylabel('Response time (miliseconds)')
    ax.set_xlabel('Backends')  
    ax.set_xticks(ind + 3*width)
    ax.set_xticklabels(('3', '5', '7'))

    plots = []

    for j, b in zip(range(0, 3), range(0, 6)[::2]):
        p1 = plt.bar(ind + j*width, vals_none[j], width, color=colors_get[j], yerr=np.array([percsl_none[j], percsh_none[j]]), error_kw=dict(capthick=1.5, lw=1.5))
        p2 = plt.bar(ind + j*width + 3*width, vals_all[j], width, color=colors_get[j], yerr=np.array([percsl_all[j], percsh_all[j]]), error_kw=dict(capthick=1.5, lw=1.5), hatch="//")
        plots.append(p1)
        plots.append(p2)

    # legend1 = plt.legend((plots[0], plots[1]), ("N = 1", "N = All"), loc=1, title="Replication", ncol=2, fancybox=True, fontsize=12)
    # plt.legend((plots[0], plots[2], plots[4]), ("1%", "5%", "10%"), loc=2, title="Writes", ncol = 3, fancybox=True, fontsize=12)
    # plt.gca().add_artist(legend1)
    
    plt.show()

# vis_logs(SET, queuet, median)
# vis_logs_err(SET, queuet)
# vis_logs_perc(GET, queuet)
# parse_logs()
# vis_logs_gs(queuet)
vis_bars_rt(returnt)