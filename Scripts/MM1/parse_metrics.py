import matplotlib.pyplot as plt
import numpy as np
import csv

folder = "/home/petar/AutumnSemester/AdvancedSystems/Milestone3/Stability/"
file_init = "run.log"

qmID = 0
tID = 1
gq_size = 2
sq_size = 1
s_jobs = 2

threads = 16

def parse_file(filename, servers):
    gets = []
    sets = []

    with open (filename, 'r') as log:
        lines = log.readlines()

        for line in lines:
            parsed_line = []
            split_line = line.split(",")
            if len(split_line) < 2:
                continue

            for t in split_line:
                parsed_line.append(int(t))     

            if (parsed_line[0] == 0):
                gets.append(parsed_line[1:])    
            else:
                sets.append(parsed_line[1:])

    gq_load, gq_size = parse_gets(gets, servers)
    sq_size, sq_jobs = parse_sets(sets, servers)
    return gq_load, gq_size, sq_size, sq_jobs

def parse_gets(gets, servers):
    gets_load = np.zeros((servers, threads), dtype=np.int)
    queues = []
    for i in range (0, servers):
        queues.append([])

    for line in gets:
        queues[line[qmID]].append(line[gq_size])
        gets_load[line[qmID]][line[tID]] += 100

    mean_queues = []
    for q in queues:
        mean_queues.append(np.mean(q))

    return gets_load, mean_queues

def parse_sets(sets, servers):
    queues_size = []
    queues_jobs = []
    for i in range (0, servers):
        queues_size.append([])
    for i in range (0, servers):
        queues_jobs.append([])

    for line in sets:
        queues_size[line[qmID]].append(line[sq_size])
        queues_jobs[line[qmID]].append(line[s_jobs])

    mean_qs = []
    mean_qj = []

    for q in queues_size:
        mean_qs.append(np.mean(q))

    for q in queues_jobs:
        mean_qj.append(np.mean(q))  

    return mean_qs, mean_qj

def write_logs(all_info):
    with open("bench_parsed_metrics.log", "w") as file:
        for inst in all_info:
            file.write("Backends: " + str(inst[0]) + " | Replication: " + str(inst[1]) + "\n")
            file.write("GETs | Queue sizes | Queue load\n")
            for i, qs, ql in zip(range(0, inst[0]), inst[3], inst[2]):
                file.write("Queue " + str(i) + ": " + str(qs) + "," + str(np.sum(ql)) + "\n")

            file.write("SETs | Queue size | Jobs in Service\n")
            for qs, js in zip(inst[4], inst[5]):
                file.write(str(qs) + "," + str(js) + "\n")
            file.write("\n")

def main():
    all_info = []

    for b in range(3, 9)[::2]:
        mid_repl = b/2 + 1
        for r in [1, mid_repl, b]:
            filename = folder + "MetricsLog_" + str(b) + "_" + str(r) + ".log"
            gq_load, gq_size, sq_size, sq_jobs = parse_file(filename, b)
            all_info.append([b, r, gq_load, gq_size, sq_size, sq_jobs])

    write_logs(all_info)

main()




