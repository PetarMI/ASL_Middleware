import argparse
import matplotlib.pyplot as plt
import numpy as np
import csv
import operator

folder = "/home/petar/AutumnSemester/AdvancedSystems/Milestone3/Stability/"
file_init = "RequestLog_stability.log"

ms = 1000000
seconds = 10**9

op = 0
s_parset = 0
f_parset = 1
s_queuet = 2
f_queuet = 3
s_pqueuet = 4
f_pqueuet = 5
s_servert = 6
f_servert = 7
s_returnenqt = 8
f_returnenqt = 9
s_returnqt = 10
f_returnqt = 11
s_totalt = 12
f_totalt = 13

GET_ratio = 100
SET_ratio = 20

def parse_file():
    gets = []
    sets = []
    all_ops = []

    with open (folder + file_init, 'r') as log:
        next(log)
        for line in log:
            parsed_line = []
            split_line = line.split(",")
            for t in split_line[1:]:
                parsed_line.append(float(t))     
            
            if (split_line[op] == "get"):
                gets.append(parsed_line)
            else:
                sets.append(parsed_line)

    numpy_gets = np.array(gets)
    numpy_sets = np.array(sets)
    all_ops = np.concatenate((numpy_gets, numpy_sets))

    return numpy_gets, numpy_sets, all_ops

def get_T(timestamps):
    start_time = timestamps[0][s_totalt]
    finish_time = timestamps[-1][f_totalt]

    T = finish_time - start_time
    return sec(T)

def get_timestamp(timestamps, s_t, f_t):
    s_times = timestamps[:,s_t]
    f_times = timestamps[:,f_t]

    times = np.subtract(f_times, s_times)
    return times

def get_lambda(arrivals, time, ratio):
    A = len(arrivals) * ratio

    return A / time

def get_mu(timestamps, es):
    service_t = get_timestamp(timestamps, f_queuet, f_returnenqt)
    
    if (es == None):
        es = sec(np.mean(service_t))

    return 1 / es

def get_ro(lam, mu):
    return lam / mu

def sec(timestamp):
    return timestamp / seconds

def main():
    gets, sets, all_ops = parse_file()
    T = get_T(gets)
    print "Runtime: " + str(T)
    lam_g = get_lambda(gets, T, GET_ratio)
    print "Arrival rate GET: " + str(lam_g)
    lam_s = get_lambda(sets, T, SET_ratio)
    print "Arrival rate SET: " + str(lam_s)

    get_mu(all_ops, None)

    mu_g = get_mu(gets, None)
    mu_s = get_mu(sets, None)    

    print "Service rate GETs: " + str(mu_g)
    print "Service rate SETs: " + str(mu_s)

    print "Traffic intensity: " + str(get_ro(11500, 0.99 * 16 * 3 * mu_g + 3 * mu_s * 0.01))

main()

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