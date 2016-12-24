import argparse
import matplotlib.pyplot as plt
from cycler import cycler

clients=[380, 400, 420, 440, 460]
tps=[]
filen="parsed_mem_var.log"

def parse_log (filename):
    with open (filename, 'r') as csvlog:
        for line in csvlog:
            split_line = line.split(",")
            tps.append(float(split_line[2]))

    fig, ax = plt.subplots()
    for x in range(0, 5):
        ax.plot(clients, tps[x::5], 'b-o')
    ax.set_xlabel("Virtual client")
    ax.set_ylabel("TPS (Gets/second)")

    plt.show()

parse_log(filen)
