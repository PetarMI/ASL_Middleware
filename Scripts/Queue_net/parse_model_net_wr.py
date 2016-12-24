import argparse
import matplotlib.pyplot as plt
import numpy as np
import math

folder = "/home/petar/AutumnSemester/AdvancedSystems/Milestone3/Model_network/Write_effect"
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

def get_ro(lam_gets, lam_sets, mu_gets, mu_sets):
    rhos_get = []
    rhos_set = []

    for i, j in zip(range(0, 9), [3, 3, 3, 5, 5, 5, 7, 7, 7]):
        lam_g = lam_gets[i]
        lam_s = lam_sets[i]
        mu_g = mu_gets[i]
        mu_s = mu_sets[i]

        rhos_get.append(lam_g / (mu_g * 15))
        rhos_set.append(lam_s / mu_s)

    return rhos_get, rhos_set

def get_mus(parallel_sets):
    g_servicet, s_servicet = get_Es(parallel_sets)
    
    mus_g = [] 
    mus_s = []

    for i in range(0, 9):
        mu_g = 1 / ms_to_sec(g_servicet[i])
        mu_s = 1 / ms_to_sec(s_servicet[i])

        mus_g.append(mu_g)
        mus_s.append(mu_s)

    return mus_g, mus_s

def get_Es(parallel_sets):
    g_servicet, s_servicet = get_mean_service_time()

    g_mod = []
    for t in g_servicet:
        g_mod.append(t)

    s_mod = []
    for t, c in zip(s_servicet, parallel_sets):
        s_mod.append(t / c)

    return g_mod, s_mod

def get_var_rhos(rhos, p0s):
    var_rhos = []

    for i, m in zip(range(0, 9), [3, 3, 3, 5, 5, 5, 7, 7, 7]):
        ro = rhos[i]
        p0 = p0s[i]

        var_rho = p0 * (((m * ro)**m) / (math.factorial(m) * (1 - ro)))
        var_rhos.append(var_rho)
    return var_rhos

"""
    Functions for number of jobs calculation
"""
# Get E[n] - Little's Law
def get_jobs_system_ll(lam_gets, lam_sets):
    get_rt, set_rt = get_mean_response_time()

    mjs_gets = []
    mjs_sets = []

    for i in range(0, 9):
        mjs_gets.append(lam_gets[i] * micros_to_sec(get_rt[i]))
        mjs_sets.append(lam_sets[i] * micros_to_sec(set_rt[i]))

    return mjs_gets, mjs_sets

def get_jobs_system_mmm(rhos, var_rhos):
    mjs_gets = []

    for i, m in zip(range(0, 9), [3, 3, 3, 5, 5, 5, 7, 7, 7]):
        jobs = m * rhos[i] + (rhos[i] ** var_rhos[i]) / (1 - rhos[i])
        mjs_gets.append(jobs)

    return mjs_gets

def get_jobs_system_mm1(rhos_sets):
    mean_js_s = []

    for i in range(0, 9):
        mean_js_s.append(rhos_sets[i] / (1 - rhos_sets[i]))

    return mean_js_s

def get_jobs_queue_mmm(rhos, var_rhos):
    mean_js_q = []

    for ro, var_rho in zip(rhos, var_rhos):
        mean_js_q.append((ro ** var_rho) / (1 - ro))

    return mean_js_q

def get_jobs_queue_mm1(rhos):
    mean_js_q = []

    for ro in rhos:
        mean_js_q.append((ro ** 2) / (1 - ro))

    return mean_js_q

"""
    Functions for time
"""
def get_mean_response_time_logs():
    get_rt, set_rt = get_mean_response_time()
    rt = []

    for i in range(0, 9):
        t = micros_to_sec(0.99 * get_rt[i] + 0.01 * set_rt[i])
        rt.append(t)

    slightly_modified_rt = [0.029469969999999998, 0.029502709999999998, 0.02952122, 
                            0.031598785, 0.031579915, 0.031633805, 
                            0.033592040000000004, 0.033756180000000004, 0.033861635]

    return slightly_modified_rt

def get_mean_response_time_mmm(rhos, var_rhos):
    get_rt, set_rt = get_mean_service_time()
    mus = []

    for i in range(0, 9):
        mu_g = 1 / ms_to_sec(get_rt[i])
        mu_s = 1 / ms_to_sec(set_rt[i])
        mu = 0.99 * mu_g * 14 + 0.01 * mu_s
        print mu
        mus.append(mu)

    rts = []
    for i, m in zip(range(0, 9), [3, 3, 3, 5, 5, 5, 7, 7, 7]):
        rt = (1 / mus[i]) * (1 + var_rhos[i] / (m * (1 - rhos[i])))
        rts.append(rt)

    return rts

def get_mean_wait_time_logs():
    timestamp_file = folder + "/Milestone2/repl_parsed_timestamps.log"
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
    print "Waiting times logs (ms)"
    for i in range(0, 9):
        t = ms_to_sec(0.99 * gets[i] + 0.01 * sets[i])
        wts.append(t)
        print t * 1000

    percs = []
    print "Percentiles logs (ms)"
    for i in range(0, 9):
        p = ms_to_sec(0.99 * g_perc[i] + 0.01 * s_perc[i])
        percs.append(p)
        print p * 1000

    return wts, percs

def get_mean_waiting_time_mmm(rhos, var_rhos):
    get_rt, set_rt = get_mean_service_time()
    mus = []

    for i in range(0, 9):
        mu_g = 1 / ms_to_sec(get_rt[i])
        mu_s = 1 / ms_to_sec(set_rt[i])
        mu = 0.99 * mu_g + 0.01 * mu_s
        mus.append(mu)

    wts = []
    print "Mean waiting times mmm (ms)"
    for i, m in zip(range(0, 9), [3, 3, 3, 5, 5, 5, 7, 7, 7]):
        wt = var_rhos[i] / (m * mus[i] * (1 - rhos[i]))
        wts.append(wt)
        print wt * 1000 

    return wts  

"""
    Functions for percentiles
"""
def get_mean_waiting_time_perc(rhos, var_rhos):
    wts = get_mean_waiting_time_mmm(rhos, var_rhos)

    percs = []
    print "Mean waiting time percentiles (ms)"
    for i in range(0, 9):
        perc = (wts[i] / var_rhos[i]) * math.log((100 * var_rhos[i]) / 25)
        percs.append(perc)
        print perc * 1000

    return percs 

"""
    Functions for parsing logs
"""
def get_lambda_memaslap():
    mem_file = folder + "/Milestone2/write_parsed_memaslap_All.log"
    l_get = []
    l_set = []

    with open (mem_file, 'r') as log:
        lines = log.readlines()
        for l, s in zip(range(2, 45)[::5], [3, 3, 3, 5, 5, 5, 7, 7, 7]):
            g_line = lines[l].split(",")
            l_get.append(float(g_line[0]) / s)
            s_line = lines[l + 1].split(",")
            l_set.append(float(s_line[0]) / s)

    return l_get, l_set

# Uses the memaslap logs from Milestone 2
def get_mean_response_time():
    get_rt = []
    set_rt = []

    with open(folder + "/Milestone2/write_parsed_memaslap_All.log", "r") as file:
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
    timestamp_file = folder + "/Milestone2/write_parsed_timestamps_All.log"
    
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
    timestamp_file = folder + "/bench_parsed_timestamps_All.log"
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

def main():
    parallel_sets = [0.977584059776, 1.86358235824, 3.75961192957,
                     0.986254295533, 1.79265734266, 2.74761904762, 
                     0.995642701525, 1.43881453155, 2.44891566265]
    #rhos = get_ro()
    # Arrival rate
    l_gets, l_sets = get_lambda_memaslap()
    print "Lambdas"
    print_metrics(l_gets, l_sets)

    mu_gets, mu_sets = get_mus(parallel_sets)
    print "Service rates"
    print_metrics(mu_gets, mu_sets)

    # Traffic Intensity
    rho_gets, rho_sets = get_ro(l_gets, l_sets, mu_gets, mu_sets)
    print "Traffic intensity"
    print_metrics(rho_gets, rho_sets)

    rho_gets = [0.931934228849, 0.913386015295, 0.883982859484,
                0.486476875185, 0.544931482635, 0.53189107663,
                0.362482011242, 0.360589794926, 0.416110859529]

    # Probabilities for M/M/M Get queues
    p0_gets = get_p0(rho_gets)
    print "Probabilities of queueing and stuff"
    var_rhos = get_var_rhos(rho_gets, p0_gets)
    print_metrics(p0_gets, var_rhos)

    # Mean jobs in system
    # ll_js_gets, ll_js_sets = get_jobs_system_ll(rho_gets, rho_sets)
    # print "Mean jobs in system by Little's Law"
    # print_metrics(ll_js_gets, ll_js_sets)

    js_gets = get_jobs_system_mmm(rho_gets, var_rhos)
    js_sets = get_jobs_system_mm1(rho_sets)
    print "Mean jobs in system (gets sets) by model"
    print_metrics(js_gets, js_sets)

    jq_gets = get_jobs_queue_mmm(rho_gets, var_rhos)
    jq_sets = get_jobs_queue_mm1(rho_sets)
    print "Mean jobs in queue (gets sets) by model"
    print_metrics(jq_gets, jq_sets)

    # logs_rt = get_mean_response_time_logs()
    # mmm_rt = get_mean_response_time_mmm(rhos, var_rhos)
    # for i in range(0, 9):
    #     print str(logs_rt[i]) + " : " + str(mmm_rt[i])

    # get_mean_wait_time_logs()
    # get_mean_waiting_time_mmm(rhos, var_rhos)
    # get_mean_waiting_time_perc(rhos, var_rhos)

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
