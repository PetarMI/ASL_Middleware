import argparse
import matplotlib.pyplot as plt

clients=[]
tps=[]

def parse_log (filename):
    with open (filename, 'r') as csvlog:
        for line in csvlog:
            split_line = line.split(",")
            tps.append(float(split_line[0]))
            clients.append(int(split_line[1]))

    fig, ax = plt.subplots()
    ax.plot(clients, tps, 'b-o')
    ax.set_xlabel("Virtual client")
    ax.set_ylabel("TPS (Gets/second)")

    plt.show()

parser = argparse.ArgumentParser()
parser.add_argument('--file', '-f', type=str)
args = parser.parse_args()
filename = args.file

parse_log(filename)

