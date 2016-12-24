import matplotlib.pyplot as plt
import numpy as np
import csv

folder="/home/petar/AutumnSemester/AdvancedSystems/ReplEffect/Memaslap/tps_logs"

def parse_instance(backends, repl):
    filename1 = folder + "/repl_" + backends + "_" + repl

    i_get_tps=[]
    i_get_std=[]
    i_get_rt=[]
    i_get_rt_std=[]
    i_set_tps=[]
    i_set_std=[]
    i_set_rt=[]
    i_set_rt_std=[]
    i_tot_tps=[]
    i_tot_std=[]
    i_tot_rt=[]
    i_tot_rt_std=[]

    for server in map(str, range(0, 3)):
        filename2 = filename1 + "_" + server

        r_get_tps=[]
        r_get_std=[]
        r_get_rt=[]
        r_get_rt_std=[]
        r_set_tps=[]
        r_set_std=[]
        r_set_rt=[]
        r_set_rt_std=[]
        r_tot_tps=[]
        r_tot_std=[]
        r_tot_rt=[]
        r_tot_rt_std=[]

        for repl in map(str, range(0, 3)):
            filename = filename2 + "_" + repl + ".log"
            gtm, gts, grm, grsd, stm, sts, srm, srsd, ttm, tts, trm, trsd = parse_replica(filename)
            
            r_get_tps.append(gtm)
            r_get_std.append(gts)
            r_get_rt.append(grm)
            r_get_rt_std.append(grsd)
            r_set_tps.append(stm)
            r_set_std.append(sts)
            r_set_rt.append(srm)
            r_set_rt_std.append(srsd)
            r_tot_tps.append(ttm)
            r_tot_std.append(tts)
            r_tot_rt.append(trm)
            r_tot_rt_std.append(trsd)

        i_get_tps.append(np.mean(r_get_tps))
        i_get_std.append(np.mean(r_get_std))
        i_get_rt.append(np.mean(r_get_rt))
        i_get_rt_std.append(np.mean(r_get_rt_std))
        i_set_tps.append(np.mean(r_set_tps))
        i_set_std.append(np.mean(r_set_std))       
        i_set_rt.append(np.mean(r_set_rt))
        i_set_rt_std.append(np.mean(r_set_rt_std))
        i_tot_tps.append(np.mean(r_tot_tps))
        i_tot_std.append(np.mean(r_tot_std))
        i_tot_rt.append(np.mean(r_tot_rt))
        i_tot_rt_std.append(np.mean(r_tot_rt_std))

    igt = np.sum(i_get_tps)
    igts = np.mean(i_get_std)
    igr = np.mean(i_get_rt)
    igrs = np.percentile(i_get_rt, 90)
    ist = np.sum(i_set_tps)
    ists = np.mean(i_set_std)
    isr = np.mean(i_set_rt)
    isrs = np.percentile(i_set_rt, 90)
    itt = np.sum(i_tot_tps)
    itts = np.mean(i_tot_std)
    itr = np.mean(i_tot_rt)
    itrs = np.percentile(i_tot_rt, 90)

    return igt, igts, igr, igrs, ist, ists, isr, isrs, itt, itts, itr, itrs

def parse_replica(file):
    get_tps=[]
    get_rt=[]
    get_rt_std=[]
    set_tps=[]
    set_rt=[]
    set_rt_std=[]
    tot_tps=[]
    tot_rt=[]
    tot_rt_std=[]

    f = open(file, 'r')
    text = f.readlines()
    for l in range (10, 110):
        pos = 10 + l*16
        
        # GET info
        period_line = text[pos]
        info = period_line.split()
        get_tps.append(int(info[3]))
        get_rt.append(int(info[8]))
        get_rt_std.append(float(info[9]))

        # SET info
        period_line = text[pos + 5]
        info = period_line.split()
        set_tps.append(int(info[3]))
        set_rt.append(int(info[8]))
        set_rt_std.append(float(info[9]))

        # TOTAL info
        period_line = text[pos + 10]
        info = period_line.split()
        tot_tps.append(int(info[3]))
        tot_rt.append(int(info[8]))
        tot_rt_std.append(float(info[9]))

    get_tps_mean = np.mean(get_tps)
    get_tps_std = np.std(get_tps)
    get_rt_mean = np.median(get_rt)
    get_rt_std_dev = np.mean(get_rt_std)
    set_tps_mean = np.mean(set_tps)
    set_tps_std = np.std(set_tps)
    set_rt_mean = np.median(set_rt)
    set_rt_std_dev = np.mean(set_rt_std)
    tot_tps_mean = np.mean(tot_tps)
    tot_tps_std = np.std(tot_tps)
    tot_rt_mean = np.median(tot_rt)
    tot_rt_std_dev = np.mean(tot_rt_std)

    return get_tps_mean, get_tps_std, get_rt_mean, get_rt_std_dev, set_tps_mean, set_tps_std, set_rt_mean, set_rt_std_dev, tot_tps_mean, tot_tps_std, tot_rt_mean, tot_rt_std_dev 

def parse_backends(backends):
    middle_repl=backends/2 + 1
    replication=[1, middle_repl, backends]
    
    get_tps=[]
    get_std=[]
    get_rt=[]
    get_rt_std=[]
    set_tps=[]
    set_std=[]
    set_rt=[]
    set_rt_std=[]
    tot_tps=[]
    tot_std=[]
    tot_rt=[]
    tot_rt_std=[]

    for repl in map(str, replication):
        igt, igts, igr, igrs, ist, ists, isr, isrs, itt, itts, itr, itrs = parse_instance(str(backends), repl)
        
        get_tps.append(igt)
        get_std.append(igts)
        get_rt.append(igr)
        get_rt_std.append(igrs)
        set_tps.append(ist)
        set_std.append(ists)
        set_rt.append(isr)
        set_rt_std.append(isrs)
        tot_tps.append(itt)
        tot_std.append(itts)
        tot_rt.append(itr)
        tot_rt_std.append(itrs)

    return get_tps, get_std, get_rt, get_rt_std, set_tps, set_std, set_rt, set_rt_std, tot_tps, tot_std, tot_rt, tot_rt_std

def parse_logs():
    get_tps=[]
    get_std=[]
    get_rt=[]
    get_rt_std=[]
    set_tps=[]
    set_std=[]
    set_rt=[]
    set_rt_std=[]
    tot_tps=[]
    tot_std=[]
    tot_rt=[]
    tot_rt_std=[]

    for backends in [3, 5, 7]:
        igt, igts, igr, igrs, ist, ists, isr, isrs, itt, itts, itr, itrs = parse_backends(backends)
        
        get_tps.append(igt)
        get_std.append(igts)
        get_rt.append(igr)
        get_rt_std.append(igrs)
        set_tps.append(ist)
        set_std.append(ists)
        set_rt.append(isr)
        set_rt_std.append(isrs)
        tot_tps.append(itt)
        tot_std.append(itts)
        tot_rt.append(itr)
        tot_rt_std.append(itrs)

    write_logs(get_tps, get_std, get_rt, get_rt_std, set_tps, set_std, set_rt, set_rt_std, tot_tps, tot_std, tot_rt, tot_rt_std)

def write_logs(get_tps, get_std, get_rt, get_rt_std, set_tps, set_std, set_rt, set_rt_std, tot_tps, tot_std, tot_rt, tot_rt_std):
    with open("parsed_percentile.log", "w") as file:
        file.write("GET" + "\n")
        file.write(",".join(map(str, range(3, 9)[::2])) + "\n")
        for b in range(0, 3): 
            file.write(",".join(map(str, get_tps[b])) + "\n")
            file.write(",".join(map(str, get_std[b])) + "\n")
            file.write(",".join(map(str, get_rt[b]))+ "\n")
            file.write(",".join(map(str, get_rt_std[b])) + "\n")
            file.write("\n")

        file.write("SET" + "\n")
        for b in range(0, 3): 
            file.write(",".join(map(str, set_tps[b])) + "\n")
            file.write(",".join(map(str, set_std[b])) + "\n")
            file.write(",".join(map(str, set_rt[b]))+ "\n")
            file.write(",".join(map(str, set_rt_std[b])) + "\n")
            file.write("\n")

        file.write("TOTAL" + "\n")
        for b in range(0, 3): 
            file.write(",".join(map(str, tot_tps[b])) + "\n")
            file.write(",".join(map(str, tot_std[b])) + "\n")
            file.write(",".join(map(str, tot_rt[b]))+ "\n")
            file.write(",".join(map(str, tot_rt_std[b])) + "\n")
            file.write("\n")

def vis_all_rt():
    rt=[[], [], []]
    repl_axis = [[1, 2, 3], [1, 3, 5], [1, 4, 7]]
    get_info = [5, 10, 15]
    set_info = [21, 26, 31]
    total_info = [36, 41, 46]

    with open("parsed_percentile.log", "r") as file:
        data = file.readlines()
        t = 0
        for l in get_info:
            split_line = data[l].split(",")
            for i in range(0, 3):
                rt[t].append(split_line[i])
            t += 1

    fig, ax = plt.subplots()
    axes = plt.gca()
    axes.set_xlim([0.5,7.5])
    ax.set_xlabel("Replication factor")
    ax.set_ylabel("Response time ()")

    j = 0
    for i in [3, 5, 7]:
        ax.plot(repl_axis[j], rt[j], '-o', label="Backends = {0}".format(i))
        j += 1

    # plt.legend(loc=1, ncol=2, prop={'size':10}, shadow=True, title="Legend", fancybox=True, fontsize=12)
    # ax.get_legend().get_title().set_color("black")

    plt.show()

def vis_rt_std():
    rt = [[], [], []]
    std = [[], [], []]
    repl_axis = [[1, 2, 3], [1, 3, 5], [1, 4, 7]]
    get_info = [4, 9, 14]
    get_std_info = [5, 10, 15]
    set_info = [20, 25, 30]
    set_std_info = [21, 26, 31]
    total_info = [36, 41, 46]
    total_std_info = [37, 42, 47]

    with open("parsed_percentile.log", "r") as file:
        data = file.readlines()
        t = 0
        for l in get_info:
            split_line = data[l].split(",")
            for i in range(0, 3):
                rt[t].append(float(split_line[i]))
            t += 1

        t = 0
        for l in get_std_info:
            split_line = data[l].split(",")
            for i in range(0, 3):
                std[t].append(float(split_line[i]))
            t += 1

    fig, ax = plt.subplots()
    axes = plt.gca()
    axes.set_xlim([0.5,7.5])
    ax.set_xlabel("Replication factor")
    ax.set_ylabel("Response time ()")

    j = 0
    for i in [3, 5, 7]:
        print rt[j]
        plt.errorbar(repl_axis[j], rt[j], std[j], marker='o', label="Backends = {0}".format(i))
        j += 1

    plt.legend(loc=1, ncol=2, prop={'size':10}, shadow=True, title="Legend", fancybox=True, fontsize=12)
    ax.get_legend().get_title().set_color("black")

    plt.show()

def vis_tps_std():
    tps = [[], [], []]
    std = [[], [], []]
    repl_axis = [[1, 2, 3], [1, 3, 5], [1, 4, 7]]
    get_info = [2, 7, 12]
    get_std_info = [3, 8, 13]
    set_info = [18, 23, 28]
    set_std_info = [19, 24, 29]
    total_info = [34, 39, 44]
    total_std_info = [35, 40, 45]

    with open("parsed_percentile.log", "r") as file:
        data = file.readlines()
        t = 0
        for l in get_info:
            split_line = data[l].split(",")
            for i in range(0, 3):
                tps[t].append(float(split_line[i]))
            t += 1

        t = 0
        for l in get_std_info:
            split_line = data[l].split(",")
            for i in range(0, 3):
                std[t].append(float(split_line[i]))
            t += 1

    fig, ax = plt.subplots()
    axes = plt.gca()
    axes.set_xlim([0.5,7.5])
    ax.set_xlabel("Replication factor")
    ax.set_ylabel("TPS (GET ops/second)")

    j = 0
    for i in [3, 5, 7]:
        plt.errorbar(repl_axis[j], tps[j], std[j], marker='o', label="Backends = {0}".format(i))
        j += 1

    plt.legend(loc=1, ncol=2, prop={'size':10}, shadow=True, title="Legend", fancybox=True, fontsize=12)
    ax.get_legend().get_title().set_color("black")

    plt.show()

vis_all_rt()
# vis_rt_std()
# vis_tps_std()
# parse_logs()