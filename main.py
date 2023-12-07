import logging
import multiprocessing
import os
import threading
from configparser import ConfigParser
from datetime import datetime

from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter

import AngFilter
import ang_rw
from TLE_to_ANG import AngCalculator
from ang_rw import read_ang


def check_dirs(directory):
    full_path = os.path.join(os.getcwd(), directory)
    if not os.path.isdir(full_path):
        os.mkdir(full_path)
    return full_path


def get_conf(filename='config.conf'):
    parser = ConfigParser(inline_comment_prefixes="#")
    parser.read(os.path.join(os.getcwd(), filename))
    conf = {}
    try:
        for section in parser.sections():
            items = parser.items(section)
            conf.update(items)
    except Exception as err:
        # logging.error(str(err))
        return
    return conf


class AngViewer:
    plt.rcParams["figure.figsize"] = [18, 8]
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['blue', 'green', 'red', 'cyan', 'magenta', 'yellow',
                                                        'black', 'purple', 'pink', 'brown', 'orange', 'teal',
                                                        'coral', 'lightblue', 'lime', 'lavender', 'turquoise',
                                                        'darkgreen', 'tan', 'salmon', 'gold'])
    plt.ylabel("Elevation")
    ax = plt.gca()
    date_form = DateFormatter("%H:%M:%S")
    ax.xaxis.set_major_formatter(date_form)

    def draw_ang(self, df, sat_number):
        df_shadow = df[df['Ph'] == 0.0]
        df_shine = df[df['Ph'] != 0.0]
        if df_shine.size != 0:
            df_shine.plot(x='Time', y='Elev', grid=True, ax=self.ax, legend=False, xlabel="Time", marker="1")
        if df_shadow.size != 0:
            df_shadow.plot(x='Time', y='Elev', grid=True, ax=self.ax, legend=False, xlabel="Time", color="grey")
        middle_time = df.iloc[df["Elev"].idxmax()]["Time"]
        min_distance = str(df["Distance"].min() / 1000).split(".")[0]
        ann = sat_number + "(" + min_distance + ")"
        self.ax.annotate(ann, xy=(middle_time, df["Elev"].max()),
                         xytext=(-15, 15), textcoords='offset points',
                         arrowprops={'arrowstyle': '->'})

    def view(self, path):
        file_list = os.listdir(path)
        for file in file_list:
            sat_number = file.split(sep='_')[0]
            self.draw_ang(read_ang(os.path.join(path, file)), sat_number)
        plt.show()


def run_calc(conf, satellites):
    threads_qty = int(conf["threads"])
    splited_salellites = list()
    processes = list()
    ang_calculator_list = list()

    manager = multiprocessing.Manager()
    lock = manager.Lock()
    global_ang_list = manager.list()

    if len(satellites) < threads_qty:
        for i in range(0, len(satellites)):
            splited_salellites.append(dict())
    else:
        for i in range(0, threads_qty):
            splited_salellites.append(dict())
    i = 0
    for key, value in satellites.items():
        splited_salellites[i].update({key: value})
        if i == len(splited_salellites) - 1:
            i = 0
        else:
            i += 1
    perf_start = datetime.now()
    for sats in splited_salellites:
        ang_calculator_list.append(AngCalculator(conf, sats))
    for ac in ang_calculator_list:
        process = multiprocessing.Process(target=ac.tle_to_ang, args=(global_ang_list, lock))
        processes.append(process)
        process.start()
    for _, process in enumerate(processes):
        process.join()
    perf = datetime.now() - perf_start
    print("Время расчета : {} sec".format(perf.seconds + perf.microseconds / 1000000))
    for items in global_ang_list:
        for item in items:
            ang_rw.write_ang(item[0], item[1], item[2])


if __name__ == '__main__':
    conf = get_conf()
    ang_dir = conf["angdirectory"]
    tle_dir = conf["tledirectory"]

    satellites = ang_rw.read_tle(tle_dir)
    run_calc(conf, satellites)

    if bool(conf["filter_by_sieve"] == "True"):  # Прореживание
        sieve = int(conf["sieve"])
        AngFilter.thin_out(ang_dir, sieve)

    app = AngViewer()  # Отображение
    app.view(ang_dir)
