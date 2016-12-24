import argparse
import matplotlib.pyplot as plt
import numpy as np
import math

folder = "/home/petar/AutumnSemester/AdvancedSystems/Milestone3/Model_network/Write_effect"

def sec(timestamp):
    seconds = 10**9
    return timestamp / seconds

def ms_to_sec(ms):
    return ms / 1000

def micros_to_sec(micros):
    return micros / 1000000

def mva(Z, M, Si):
    N = 360
    Vi = 1.0 / M
    Q = np.zeros(M)

    for n in range(0, N):
        R_sys = 0
        X_sys = 0
        R = np.zeros(M)

        for i in range(0, M):
            R[i] = Si * (1 + ((N - 1) / N) * Q[i])

        for i in range(0, M):
            R_sys += R[i]*Vi

        X_sys = N / (Z + R_sys)

        for i in range(0, M):
            Q[i] = X_sys * Vi * R[i]

    # Device TPS and Utilization
    Xi = X_sys * Vi
    Ui = X_sys * Si * Vi

    return Xi, Ui

def mva_giac(m, Z):
    N = 361
    rs = [
        {
            "GET Q": 0,
            "SET Q": 0,
            "Answer Q": 0
        }
    ]

    for n in range(1, N):
        r = {}
        r["N"] = (n)
        r["GET R"] = (m["S_gq"] * (1 + rs[-1]["GET Q"]))
        r["SET R"] = (m["S_sq"] * (1 + rs[-1]["SET Q"]))
        r["Answer R"] = (m["S_a"] * (1 + rs[-1]["Answer Q"]))

        r["System R"] = (r["GET R"] * m["vr_gq"] + r["SET R"] * m["vr_sq"] + r["Answer R"] * m["vr_a"])
        r["System R"] = (r["GET R"] + r["SET R"] + r["Answer R"])

        r["Throughput"] = (n / (r["System R"] + Z))
        r["GET Q"] = (r["Throughput"] * r["GET R"] * m["vr_gq"])
        r["SET Q"] = (r["Throughput"] * r["SET R"] * m["vr_sq"])
        r["Answer Q"] = (r["Throughput"] * r["Answer R"] * m["vr_a"])
        rs.append(r)

    return rs

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

def get_mean_respq_time():
    timestamp_file = folder + "/bench_parsed_timestamps_All.log"
    get_rq = []
    set_rq = []

    with open (timestamp_file, 'r') as log:
        lines = log.readlines() 

        for l in range(7, 153)[::17]:
            line = map(float, lines[l].split(","))
            get_rq.append(line[0])
            line = map(float, lines[l + 8].split(","))
            set_rq.append(line[0])

    resp_queue_st = []
    for i, rat in zip(range(0, 9), [0.99, 0.95, 0.9, 0.99, 0.95, 0.9, 0.99, 0.95, 0.9]):
        resp_queue_st.append(rat * get_rq[i] + (1 - rat) * set_rq[i])

    return resp_queue_st

# General fucntion for finding the service time for gets and sets
# Service time is from leaving the queue until response is queued back for sending
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
    # Arrival rate
    l_gets, l_sets = get_lambda_memaslap()
    print "Lambdas"
    print_metrics(l_gets, l_sets)

    parallel_sets = [0.977584059776, 1.86358235824, 3.75961192957,
                     0.986254295533, 1.79265734266, 2.74761904762, 
                     0.995642701525, 1.43881453155, 2.44891566265]

    Z = [0.000546986871975, 0.000562641408238, 0.00113223602941,
         0.000713892450833, 0.000843275395969, 0.0010302011043,
         0.00106524736903, 0.000847268361263, 0.000925057824775]

    M = [3, 3, 3, 5, 5, 5, 7, 7, 7]

    Sg, Ss = get_mean_service_time()
    print "Service times"
    print_metrics(Sg, Ss)

    Sa = get_mean_respq_time()
    print "Response queue times"
    print_metrics(Sa, None)

    # for i in range(0, 9):
    #     Xi, Ui = mva(Z[i], M[i], ms_to_sec(Sg[i] / 15))
    #     print str(Xi) + " " + str(Ui)

    input_config = {
        "S_gq": ms_to_sec(Sg[-1] / 15),
        "S_sq": ms_to_sec(Ss[-1] / parallel_sets[-1]),
        "S_a": ms_to_sec(Sa[-1]),
        "vr_gq": 0.1415,
        "vr_sq": 0.01,
        "vr_a": 1
    }

    print input_config

    res = mva_giac(input_config, Z[-1])
    print "MVA results"
    print res[-1]
    print "Utilization"
    U = res[-1]["Throughput"]* 0.1415 * res[-1]["GET R"]
    print U

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

