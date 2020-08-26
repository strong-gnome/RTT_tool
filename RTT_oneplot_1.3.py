"""
Made by officer_pupsik
Sometimes adjusted by strong_gnome

Python script to check RTT by HTTPS and ICMP tools to designated URLs/IP addresses.
Addresses and URLs are taken from resource.txt which is mandatory to get script working.

Version log:
1.1
Error handling is implemented, but the real-time animation is stuck sometimes. Unstable work of animation.
No HTTPS errors logging.

1.2
HTTPS logging added.
Whole process of the collecting data and plotting is reforged.
CSV collecting format implemented instead of TXT before.
Animation is stable and working with no issues.

1.3
Increased font size for the legend on the plots. Now you shouldn't strain your eyes to check legend.
ZIP function added. Now all CSV and logs are archiving into basic .zip with no compression.

"""


import csv
import pandas as pd
import os
import requests
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as pltdates
import time
import tkinter as tk
import threading
import itertools
import zipfile
from datetime import datetime
from pythonping import ping

input_file = open('resources.txt').read().splitlines()
fieldNames = []

fig, ax = plt.subplots(2, figsize=(11, 8))
fig.tight_layout(pad=2.5)

def zip_func(out_file = 'rtt_data',*filenames):
    """
    Function to zip any files with certain output name in format:
    Day-Month-Year_Hours-Minutes-Seconds_*type of data inside*.zip
    """

    if os.path.isfile(filenames[0]):
        right_now = datetime.now()
        right_now = right_now.strftime('%d-%b-%Y_%H-%M-%S_')
        with zipfile.ZipFile(right_now+out_file+'.zip', mode='w') as zip_file:
            for filename in filenames:
                try:
                    zip_file.write(filename)
                except:
                    continue

class RoundTripTest(object):
    def __init__(self, url_list):
        self.url_list = url_list
        fieldNames = []

        for url in self.url_list:
            fieldNames.append(url + '_RTT')
            fieldNames.append(url + '_TimeStamp')

        with open('https_rtt_data.csv', 'w') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldNames)
            csv_writer.writeheader()
        with open('http_log.log', 'w') as log_file:
            log_file.close()

    def __call__(self, url_list):
        self.url_list = url_list
        self.rtt_test_list = []
        fieldNames = []
        info = {}

        for url in self.url_list:
            fieldNames.append(url + '_RTT')
            fieldNames.append(url + '_TimeStamp')
        
        for url in self.url_list:
            try:
                req = requests.get(url)
                rtt = req.elapsed.total_seconds()
                resp_timestamp = datetime.now().strftime('%H:%M:%S')
                rtt = f'{rtt:.3f}'
                rtt = float(rtt)
                info[url + '_RTT'] = rtt
                info[url + '_TimeStamp'] = resp_timestamp

            except requests.exceptions.RequestException as e:
                resp_timestamp = datetime.now().strftime('%H:%M:%S')
                rtt = 0.0
                info[url + '_RTT'] = rtt
                info[url + '_TimeStamp'] = resp_timestamp

                with open('http_log.log', 'a') as log_file:
                    log_file.write(url + ':' + resp_timestamp + ':' + str(e) + '\n')
                    log_file.close()

        with open('https_rtt_data.csv', 'a', newline='') as output_file:
            csv_writer = csv.DictWriter(output_file, fieldnames=fieldNames)
            csv_writer.writerow(info)


class PingTest(object):
    def __init__(self, url_list):
        self.url_list = url_list
        fieldNames = []

        for url in self.url_list:
            fieldNames.append(url + '_RTT')
            fieldNames.append(url + '_TimeStamp')

        zip_func('rtt_data', 'http_log.log', 'icmp_rtt_data.csv', 'https_rtt_data.csv')
        with open('icmp_rtt_data.csv', 'w') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldNames)
            csv_writer.writeheader()

    def __call__(self, url_list):
        self.url_list = url_list
        self.rtt_test_list = []
        fieldNames = []
        info = {}

        for url in self.url_list:
            fieldNames.append(url + '_RTT')
            fieldNames.append(url + '_TimeStamp')

        for url in self.url_list:
            try:
                splitedURL = url.split('//', 2)
                req = ping(splitedURL[1], count=1, timeout=1)
                for request in req:
                    rtt = f'{request.time_elapsed:.3f}'
                    error = request.error_message
                if error is None:
                    rtt = float(rtt)
                    resp_timestamp = datetime.now().strftime('%H:%M:%S')
                    info[url + '_RTT'] = rtt
                    info[url + '_TimeStamp'] = resp_timestamp
                else:
                    resp_timestamp = datetime.now().strftime('%H:%M:%S')
                    rtt = 0.0
                    info[url + '_RTT'] = rtt
                    info[url + '_TimeStamp'] = resp_timestamp

            except:
                resp_timestamp = datetime.now().strftime('%H:%M:%S')
                rtt = 0.0
                info[url + '_RTT'] = rtt
                info[url + '_TimeStamp'] = resp_timestamp

        with open('icmp_rtt_data.csv', 'a', newline='') as output_file:
            csv_writer = csv.DictWriter(output_file, fieldnames=fieldNames)
            csv_writer.writerow(info)


def collect_data():
    ping_url = PingTest(input_file)
    test_url = RoundTripTest(input_file)

    while True:
        ping_url(input_file)
        test_url(input_file)


def draw(i):
    dataHttp = pd.read_csv('https_rtt_data.csv')
    dataIcmp = pd.read_csv('icmp_rtt_data.csv')
    ax[0].cla()
    ax[1].cla()

    for url in input_file:
        xAxisHttp = []
        yAxisHttp = []
        yAxisHttp = dataHttp[url + '_RTT']
        xAxisHttp = pd.to_datetime(dataHttp[url + '_TimeStamp'])
        ax[0].plot(xAxisHttp, yAxisHttp, picker=5)
        ax[0].legend(input_file, loc='upper left', prop={'size': 7})
        ax[0].xaxis.set_major_formatter(pltdates.DateFormatter('%H:%M:%S'))
        ax[0].xaxis.set_minor_formatter(pltdates.DateFormatter('%H:%M:%S'))
        ax[0].xaxis.set_major_locator(plt.MaxNLocator(9))
        ax[0].set_xlabel('Time')
        ax[0].set_ylabel('HTTPS RTT(s)')
        ax[0].grid(True, which='both')
    
        xAxisIcmp = []
        yAxisIcmp = []
        yAxisIcmp = dataIcmp[url + '_RTT']
        xAxisIcmp = pd.to_datetime(dataIcmp[url + '_TimeStamp'])
        ax[1].plot(xAxisIcmp, yAxisIcmp, picker=5)
        ax[1].legend(input_file, loc='upper left', prop={'size': 7})
        ax[1].xaxis.set_major_formatter(pltdates.DateFormatter('%H:%M:%S'))
        ax[1].xaxis.set_minor_formatter(pltdates.DateFormatter('%H:%M:%S'))
        ax[1].xaxis.set_major_locator(plt.MaxNLocator(9))
        ax[1].set_xlabel('Time')
        ax[1].set_ylabel('ICMP RTT(s)')
        ax[1].grid(True, which='both')


def show_online():
    thread = threading.Thread(target=collect_data)
    thread.start()
    animate = animation.FuncAnimation(fig, draw, interval=2000)
    plt.show()


def show_offline():
    draw(itertools.count)
    fig.canvas.mpl_connect('pick_event', on_pick)
    plt.show()


def on_pick(event):
    thisline = event.artist
    xdata = thisline.get_xdata()
    ydata = thisline.get_ydata()
    ind = event.ind
    points = tuple(zip(pd.to_datetime(xdata[ind]).strftime('%H:%M:%S'), ydata[ind]))

    if thisline.get_linewidth() == 1.5:
        thisline.set_linewidth(2.5)
    else:
        thisline.set_linewidth(1.5)
    fig.canvas.draw()


root = tk.Tk()
frame = tk.Frame(root)
frame.pack()
root.minsize(250, 100)


def close_window_online():
    root.destroy()
    show_online()


def close_window_show_offline():
    root.destroy()
    show_offline()


def close_window_wo_graph():
    root.destroy()
    collect_data()


onlineButton = tk.Button(frame, text='Collect and Show Online', command=close_window_online, height=1, width=20)
onlineButton.grid(row=0, column=0, pady=5)

offCollButton = tk.Button(frame, text='Collect Data w/o Graph', command=close_window_wo_graph, height=1, width=20)
offCollButton.grid(row=1, column=0, pady=5)

offShowButton = tk.Button(frame, text='Show Offline', command=close_window_show_offline, height=1, width=20)
offShowButton.grid(row=2, column=0, pady=5)

root.mainloop()
