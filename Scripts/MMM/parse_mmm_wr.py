import argparse
import matplotlib.pyplot as plt
import numpy as np
import math

file_init = "RequestLog_stability.log"

ms = 1000000
seconds = 10**9

def sec(timestamp):
    return timestamp / seconds

def ms_to_sec(ms):
    return ms / 1000

def micros_to_sec(micros):
    return micros / 1000000

"""
    Functions for core metrics - p0 , rho and var_rho
"""
def get_p0(rhos):
    p0s = []

    for i, m in zip(range(0, 9), [3, 3, 3, 5, 5, 5, 7, 7, 7]):
        ro = rhos[i]
        p0 = 1 + ((m * ro)**m) / (math.factorial(m) * (1 - ro))

        sig_sum = 0
        for n in range(1, m):
            sig_sum += ((m * ro)**n) / math.factorial(n)

        p0 += sig_sum
        p0 = p0**(-1)
        p0s.append(p0)

    return p0s 

def get_ro(lambdas, mus):
    rhos = []
    for i, m in zip(range(0, 9), [3, 3, 3, 5, 5, 5, 7, 7, 7]):
        lam = lambdas[i]
        mu = mus[i]
        rhos.append(lam / (m * mu))

    return rhos

def get_mus(parallel_sets):
    # g_servicet, s_servicet = get_mean_service_time()
    g_servicet, s_servicet = get_Es(15, parallel_sets)
    writes = [0.99, 0.95, 0.9, 0.99, 0.95, 0.9, 0.99, 0.95, 0.9]
    # writes = [0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99]
    
    mus = []
    for i in range(0, 9):
        mu_g = 1 / ms_to_sec(g_servicet[i])
        # mu_g *= 15
        mu_s = 1 / ms_to_sec(s_servicet[i])
        # mu_s *= parallel_sets[i]

        mus.append(writes[i] * mu_g + (1 - writes[i]) * mu_s)

    return mus

def get_Es(active_threads, parallel_sets):
    g_servicet, s_servicet = get_mean_service_time()

    g_mod = []
    for t in g_servicet:
        g_mod.append(t / active_threads)

    s_mod = []
    for t, c in zip(s_servicet, parallel_sets):
        s_mod.append(t / c)

    return g_mod, s_mod

def get_var_rhos(rhos, p0s):
    var_rhos = []

    for i, m in zip(range(0, 9), [3, 3, 3, 5, 5, 5, 7, 7, 7]):
        ro = rhos[i]
        p0 = p0s[i]

        var_rho = p0 * ((m * ro)**m) / (math.factorial(m) * (1 - ro))
        var_rhos.append(var_rho)

    return var_rhos

"""
    Functions for number of jobs calculation
"""
# Get E[n] - Little's Law
def get_jobs_system_ll(lambdas):
    get_rt, set_rt = get_mean_response_time()

    rt = []
    for i in range(0, 9):
        rt.append(micros_to_sec(0.99 * get_rt[i] + 0.01 * set_rt[i]))

    mean_js = []
    for i in range(0, 9):
        mean_js.append(lambdas[i] * rt[i])

    return mean_js

def get_jobs_system_mmm(rhos, var_rhos):
    mean_js = []
    for i, m in zip(range(0, 9), [3, 3, 3, 5, 5, 5, 7, 7, 7]):
        i_jobs = m * rhos[i] + (rhos[i]**var_rhos[i]) / (1 - rhos[i])
        mean_js.append(i_jobs)

    return mean_js

def get_jobs_queue_mmm(rhos, var_rhos):
    mean_js_q = []

    for ro, var_rho in zip(rhos, var_rhos):
        mean_js_q.append((ro ** var_rho) / (1 - ro))

    return mean_js_q

"""
    Functions for time
"""
def get_mean_response_time_mmm(mus, rhos, var_rhos):
 
    rts = []
    for i, m in zip(range(0, 9), [3, 3, 3, 5, 5, 5, 7, 7, 7]):
        rt = (1 / mus[i]) * (1 + var_rhos[i] / (m * (1 - rhos[i])))
        rts.append(rt * 1000)

    return rts

def get_mean_wait_time_logs():
    timestamp_file = "/home/petar/AutumnSemester/AdvancedSystems/Milestone3/MMM/Milestone2/write_parsed_timestamps_All.log"
    gets = []
    sets = []
    g_perc = []
    s_perc = []

    mean = 0
    med = 1
    perc = 2

    with open (timestamp_file, 'r') as log:
        lines = log.readlines()
        for l in range(3, 120)[::14]:
            g_w = 0
            s_w = 0
            g_err = 0
            s_err = 0
            line = map(float, lines[l].split(","))
            g_w += line[mean]
            g_err += line[perc]
            line = map(float, lines[l + 1].split(","))
            g_w += line[mean]
            g_err += line[perc]
            gets.append(g_w)
            g_perc.append(g_err)
            line = map(float, lines[l + 6].split(","))
            s_w += line[mean]
            s_err += line[perc]
            line = map(float, lines[l + 7].split(","))
            s_w += line[mean]
            s_err += line[perc]
            sets.append(s_w)
            s_perc.append(s_err)
    
    wts = []
    for i in range(0, 9):
        t = ms_to_sec(0.99 * gets[i] + 0.01 * sets[i])
        wts.append(t)

    percs = []
    for i in range(0, 9):
        p = ms_to_sec(0.99 * g_perc[i] + 0.01 * s_perc[i])
        percs.append(p)

    return wts, percs

def get_mean_waiting_time_mmm(mus, rhos, var_rhos):
    get_rt, set_rt = get_mean_service_time()

    wts = []
    for i, m in zip(range(0, 9), [3, 3, 3, 5, 5, 5, 7, 7, 7]):
        wt = var_rhos[i] / (m * mus[i] * (1 - rhos[i]))
        wts.append(wt)

    return wts  

"""
    Functions for percentiles
"""
def get_mean_waiting_time_perc(rhos, var_rhos, mus):
    wts = get_mean_waiting_time_mmm(mus, rhos, var_rhos)

    percs = []
    for i in range(0, 9):
        perc = (wts[i] / var_rhos[i]) * math.log((100 * var_rhos[i]) / 25)
        percs.append(perc)

    return percs 

"""
    Functions for parsing logs
"""
def get_lambda_memaslap():
    mem_file = "/home/petar/AutumnSemester/AdvancedSystems/Milestone3/MMM/Milestone2/write_parsed_memaslap_All.log"
    lambdas = []

    with open (mem_file, 'r') as log:
        lines = log.readlines()
        for l in range(4, 46)[::5]:
            line = lines[l].split(",")
            lambdas.append(float(line[0]))

    return lambdas

def get_mean_response_time_logs():
    get_rt, set_rt = get_mean_response_time()
    rt = []

    for i in range(0, 9):
        t = micros_to_sec(0.99 * get_rt[i] + 0.01 * set_rt[i])
        rt.append(t)

    return rt

# Uses the memaslap logs from Milestone 2
def get_mean_response_time():
    get_rt = []
    set_rt = []

    with open("/home/petar/AutumnSemester/AdvancedSystems/Milestone3/MMM/Milestone2/write_parsed_memaslap_All.log", "r") as file:
        data = file.readlines()

        for i in range(0, 9): 
            pos = 2 + 5*i
            info_line = data[pos].split(",")
            val = float(info_line[2])

            get_rt.append(val)

        for i in range(0, 9): 
            pos = 3 + 5*i
            info_line = data[pos].split(",")
            val = float(info_line[2])

            set_rt.append(val)

    return get_rt, set_rt

def get_mean_service_time():
    mean = 0
    med = 1
    perc = 2

    g_servert, s_servert = get_servert_timestamps()
    g_ret, s_proc, s_ret = get_bench_timestamps()

    g_servicet = []
    s_servicet = []

    for t in zip(g_servert, g_ret):
        time = t[0][mean] + t[1][mean]
        g_servicet.append(time)

    for t in zip(s_servert, s_proc, s_ret):
        time = t[0][mean] + t[1][mean] + t[2][mean]
        s_servicet.append(time)

    return g_servicet, s_servicet

# Get the server time from original experiment
def get_servert_timestamps():
    timestamp_file = "/home/petar/AutumnSemester/AdvancedSystems/Milestone3/MMM/Milestone2/write_parsed_timestamps_All.log"
    gets = []
    sets = []

    with open (timestamp_file, 'r') as log:
        lines = log.readlines()
        for l in range(5, 120)[::14]:
            line = map(float, lines[l].split(","))
            gets.append(line)
            line = map(float, lines[l + 6].split(","))
            sets.append(line)

    return gets, sets

# Get process time and return to queue time from microbenchmark 
def get_bench_timestamps():
    timestamp_file = "/home/petar/AutumnSemester/AdvancedSystems/Milestone3/MMM/bench_parsed_timestamps_All.log"
    gets = []
    sets_proc = []
    sets_ret = []

    with open (timestamp_file, 'r') as log:
        lines = log.readlines()
        for l in range(6, 153)[::17]:
            line = map(float, lines[l].split(","))
            gets.append(line)
            line = map(float, lines[l + 6].split(","))
            sets_proc.append(line)
            line = map(float, lines[l + 8].split(","))
            sets_ret.append(line)

    return gets, sets_proc, sets_ret

"""
    Visualization functions
"""
def vis_ro():
    colors_get = ['forestgreen', 'indigo', 'firebrick']

    values = [ [0.772787771309, 0.619994140792, 0.504470921803], 
               [0.788110143896, 0.667699961215, 0.537559966773], 
               [0.8168370389, 0.699200141303, 0.54946439682] ]

    fig, ax = plt.subplots()
    ind = np.arange(3) 
    width = 0.15   
    ax.set_ylabel('Traffic intensity')
    ax.set_xlabel('Backends')  
    ax.set_xticks(ind + 1.5*width)
    ax.set_xticklabels(('3', '5', '7'))

    plots = []

    for b in range(0, 3):
        p1 = plt.bar(ind, values[0], width, color=colors_get[0])
        p2 = plt.bar(ind + width, values[1], width, color=colors_get[1])
        p3 = plt.bar(ind + 2*width, values[2], width, color=colors_get[2])
        plots.append(p1)
        plots.append(p2)
        plots.append(p3)

    legend1 = plt.legend((plots[0], plots[1], plots[2]), ("N = 1", "N = Half", "N = All"), loc=1, title="Replication", ncol=2, fancybox=True, fontsize=12)
    plt.show()

def vis_jobs():
    colors_get = ['forestgreen', 'royalblue', 'firebrick']

    js_logs = [ [8.40437696757, 4.29678102749, 4.14629588661],
                [9.21141349723, 5.01395591722, 4.27089268121],
                [10.1582218129, 5.18404574381, 5.04719915197] ]

    js_mmm = [ [72, 39.75, 32], 
               [68.5, 47, 38], 
               [54.5, 59, 40] ]

    fig, ax = plt.subplots()
    ind = np.arange(3) 
    width = 0.15   
    ax.set_ylabel('Jobs in System')
    ax.set_xlabel('Backends')  
    ax.set_xticks(ind + 1.5*width)
    ax.set_xticklabels(('3', '5', '7'))

    plots = []

    for b in range(0, 3):
        p1 = plt.bar(ind, js_mmm[0], width, color=colors_get[0])
        p4 = plt.bar(ind, js_logs[0], width, color=colors_get[0], hatch="//")
        p2 = plt.bar(ind + width, js_mmm[1], width, color=colors_get[1])
        p5 = plt.bar(ind + width, js_logs[1], width, color=colors_get[1], hatch="//")
        p3 = plt.bar(ind + 2*width, js_mmm[2], width, color=colors_get[2])
        p6 = plt.bar(ind + 2*width, js_logs[2], width, color=colors_get[2], hatch="//")
        plots.append(p1)
        plots.append(p2)
        plots.append(p3)
        plots.append(p4)
        plots.append(p5)
        plots.append(p6)

    legend1 = plt.legend((plots[0], plots[1], plots[2], plots[3], plots[4], plots[5]), 
        ("Real N = 1", "Real N = Half", "Real N = All", "Model N = 1", "Model N = Half", "Model N = All"), loc=1, 
        title="Replication", ncol=2, fancybox=True, fontsize=12)
    plt.show()


def vis_wt():
    colors_get = ['forestgreen', 'royalblue', 'firebrick']

    wt_logs = [ [2.72270303427, 1.36097432266, 0.990086913734],
                [2.86436126305, 1.47418831037, 1.12833885748],
                [2.99867460229, 1.68983905082, 1.22527604325] ]

    wt_mmm = [ [2.51884139758, 0.694264610716, 0.107182957858], 
               [2.74368909761, 0.851533639945, 0.169288066682], 
               [2.88650726485, 1.02798710168, 0.184740098849] ]

    perc_logs = [ [1.27295825, 0.522862, 0.23712],
                 [1.5003665, 0.61525425, 0.3019985],
                 [1.6199345, 0.7066435, 0.3900775] ]

    perc_mmm = [ [1.03219249325, 0.0945709719247, 0],
                 [1.26410596293, 0.706122506843, 0],
                 [1.57747741581, 1.0270312593, 0] ]

    fig, ax = plt.subplots()
    ind = np.arange(3) 
    width = 0.15   
    ax.set_ylabel('Waiting time (ms)')
    ax.set_xlabel('Backends')  
    ax.set_xticks(ind + 1.5*width)
    ax.set_xticklabels(('3', '5', '7'))

    plots = []

    for b in range(0, 3):
        p1 = plt.bar(ind, wt_logs[0], width, color=colors_get[0], yerr=np.array([np.zeros(3), perc_logs[0]]), error_kw=dict(capthick=1.5, lw=1.5))
        p4 = plt.bar(ind, wt_mmm[0], width, color=colors_get[0], yerr=np.array([np.zeros(3), perc_mmm[0]]), error_kw=dict(capthick=1.5, lw=1.5), hatch="//")
        p2 = plt.bar(ind + width, wt_logs[1], width, color=colors_get[1], yerr=np.array([np.zeros(3), perc_logs[1]]), error_kw=dict(capthick=1.5, lw=1.5))
        p5 = plt.bar(ind + width, wt_mmm[1], width, color=colors_get[1], yerr=np.array([np.zeros(3), perc_mmm[1]]), error_kw=dict(capthick=1.5, lw=1.5), hatch="//")
        p3 = plt.bar(ind + 2*width, wt_logs[2], width, color=colors_get[2], yerr=np.array([np.zeros(3), perc_logs[2]]), error_kw=dict(capthick=1.5, lw=1.5))
        p6 = plt.bar(ind + 2*width, wt_mmm[2], width, color=colors_get[2], yerr=np.array([np.zeros(3), perc_mmm[2]]), error_kw=dict(capthick=1.5, lw=1.5), hatch="//")
        plots.append(p1)
        plots.append(p2)
        plots.append(p3)
        plots.append(p4)
        plots.append(p5)
        plots.append(p6)

    legend1 = plt.legend((plots[0], plots[1], plots[2], plots[3], plots[4], plots[5]), 
        ("Real N = 1", "Real N = Half", "Real N = All", "Model N = 1", "Model N = Half", "Model N = All"), loc=1, 
        title="Replication", ncol=2, fancybox=True, fontsize=12)
    plt.show()

def main():
    parallel_sets = [0.977584059776, 1.86358235824, 3.75961192957,
                     0.986254295533, 1.79265734266, 2.74761904762, 
                     0.995642701525, 1.43881453155, 2.44891566265]
    #rhos = get_ro()
    lambdas = get_lambda_memaslap()

    mus = get_mus(parallel_sets)

    rhos = get_ro(lambdas, mus)
    print rhos
    # rhos = [0.848546771779, 0.864612487496, 0.879683565708, 
    #         0.496195234277, 0.579240420247, 0.596803365243,
    #         0.369763628278, 0.383306709793, 0.465010924175]


    p0s = get_p0(rhos)
    print "Probabilities of 0 jobs in system"
    var_rhos = get_var_rhos(rhos, p0s)
    print_metrics(p0s, var_rhos)

    mj_sys = get_jobs_system_mmm(rhos, var_rhos)
    mj_queue = get_jobs_queue_mmm(rhos, var_rhos)
    print "Mean jobs in system"
    print_metrics(mj_sys, mj_queue)

    logs_rt = get_mean_response_time_logs()
    mmm_rt = get_mean_response_time_mmm(mus, rhos, var_rhos)
    print "Mean response time"
    print_metrics(logs_rt, mmm_rt)

    print "Waiting time"
    wt_real, wt_perc_real = get_mean_wait_time_logs()
    wt_mmm = get_mean_waiting_time_mmm(mus, rhos, var_rhos)
    wt_perc = get_mean_waiting_time_perc(rhos, var_rhos, mus)
    print_metrics([n * 1000 for n in wt_real], [n * 1000 for n in wt_mmm])
    print "Percentiles"
    print_metrics(wt_perc, None)

def print_metrics(gets, sets):
    if sets == None:
        for g in gets:
            print str(g)       
    elif gets == None:
        for s in sets:
            print str(s)    
    else:
        for g, s in zip(gets, sets):
            print str(g) + " " + str(s)

    print ""

main()
# vis_jobs()
# sets in service 
# [0.993781094527, 0.970624235006, 0.977584059776]
# [1.67365967366, 1.82358235824, 2.06036324786]
# [3.07784881534, 3.02057380143, 3.25961192957]
# [0.986254295533, 1.0790960452, 1.06540697674, 1.02457757296, 0.955357142857]
# [1.80375130254, 1.79265734266, 1.72604735883, 1.65563969709, 1.70617760618]
# [2.74761904762, 3.02298598949, 2.74532544379, 2.98749441715, 2.39282889533]
# [1.01165048544, 1.01346153846, 0.932038834951, 0.973933649289, 0.979910714286, 0.995642701525, 1.07281553398]
# [1.36957631445, 1.43530499076, 1.41505695889, 1.52120383037, 1.43881453155, 1.68348093955, 1.40925449871]
# [2.44891566265, 2.59108138239, 2.08663436877, 1.96073619632, 1.93324816353, 2.02416740348, 2.09971590909]

# parallel_sets = [0.977584059776, 1.86358235824, 3.75961192957,
#                  0.986254295533, 1.79265734266, 2.74761904762, 
#                  0.995642701525, 1.43881453155, 2.44891566265]
