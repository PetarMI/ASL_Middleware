import argparse
import matplotlib.pyplot as plt
import numpy as np
import csv

file_replicas = ["Timestamps/VarThreads/RequestLog_72_0.log"]#, "Timestamps/RequestLog_100_1.log", "Timestamps/RequestLog_100_2.log"]

get_times = ["Parse_T", "Queue_T", "Server_T", "Return_T", "Total_T"]
get_parse_time = []
get_queue_time = []
get_server_time = []
get_return_time = []
get_total_time = []

set_times = ["Parse_T", "Queue_T", "Process_T", "Server_T", "Return_T", "Total_T"]
set_parse_time = []
set_queue_time = []
set_process_time = []
set_server_time = []
set_return_time = []
set_total_time = []

mean_gets=[]
std_gets=[]
mean_sets=[]
std_sets=[]

ms=1000000

def parse_logs ():
    for file in file_replicas:
        with open (file, 'r') as csvlog:
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

    print ""
    mean_gets.append(np.mean(get_parse_time))
    mean_gets.append(np.mean(get_queue_time))
    mean_gets.append(np.mean(get_server_time))
    mean_gets.append(np.mean(get_return_time))
    mean_gets.append(np.mean(get_total_time))
    mean_sets.append(np.mean(set_parse_time))
    mean_sets.append(np.mean(set_queue_time))
    mean_sets.append(np.mean(set_process_time))
    mean_sets.append(np.mean(set_server_time))
    mean_sets.append(np.mean(set_return_time))
    mean_sets.append(np.mean(set_total_time))

    std_gets.append(np.std(get_parse_time))
    std_gets.append(np.std(get_queue_time))
    std_gets.append(np.std(get_server_time))
    std_gets.append(np.std(get_return_time))
    std_gets.append(np.std(get_total_time))
    std_sets.append(np.std(set_parse_time))
    std_sets.append(np.std(set_queue_time))
    std_sets.append(np.std(set_process_time))
    std_sets.append(np.std(set_server_time))
    std_sets.append(np.std(set_return_time))
    std_sets.append(np.std(set_total_time))

    with open("Timestamps/parsed_timestamps_360_.log", "w") as file:
        file.write("GETs\n")
        file.write(" | ".join(get_times) + "\n")
        file.write(" | ".join(map(str, mean_gets)) + "\n")
        file.write(" | ".join(map(str, std_gets))  + "\n")
        file.write("SETs\n")
        file.write(" | ".join(set_times) + "\n")
        file.write(" | ".join(map(str, mean_sets)) + "\n")
        file.write(" | ".join(map(str, std_sets)) + "\n")

parse_logs()
