import argparse
import matplotlib.pyplot as plt
import numpy as np
import csv
import operator

folder = "/home/petar/AutumnSemester/AdvancedSystems/Milestone3/Stability/"
file_init = "RequestLog_init.log"

ms = 1000000
seconds = 10**9
T = 3600

op = 0
parset = 0
queuet = 1
pqueuet = 2
servert = 3
returnt = 4
totalt = 5

GET_ratio = 100
SET_ratio = 100

def parse_file():
    gets = []
    sets = []

    with open (folder + file_init, 'r') as log:
        next(log)
        for line in log:
            parsed_line = []
            split_line = line.split(",")
            for t in split_line[1:-1]:
                parsed_line.append(float(t))     
            
            if (split_line[op] == "true"):
                gets.append(parsed_line)
            else:
                sets.append(parsed_line)

    numpy_gets = np.array(gets)
    numpy_sets = np.array(sets)

    return numpy_gets, numpy_sets

def get_timestamp(timestamps, t):
    times = timestamps[:,t]

    return times

def get_lambda(arrivals, time, ratio):
    A = len(arrivals) * ratio

    return A / time

def get_mu(timestamps):
    service_t = 0.0
    service_t += np.mean(get_timestamp(timestamps, pqueuet))
    service_t += np.mean(get_timestamp(timestamps, servert))
    service_t += np.mean(get_timestamp(timestamps, returnt))

    return 1 / sec(service_t)

def sec(timestamp):
    return timestamp / seconds

def main():
    gets, sets = parse_file()
    lam_g = get_lambda(gets, T, GET_ratio)
    lam_s = get_lambda(sets, T, SET_ratio)

    mu_g = get_mu(gets)
    mu_s = get_mu(sets)    

    print lam_g
    print lam_s
    print mu_g
    print mu_s

main()