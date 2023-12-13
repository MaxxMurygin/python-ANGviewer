import logging
import multiprocessing
import os
from configparser import ConfigParser
from datetime import datetime
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
import file_operations
import downloader
from TLE_to_ANG import AngCalculator
from file_operations import read_ang
from manager import EffectiveManager


def dict_from_df(cat_df):
    sat_dict = dict()
    for index, sat in cat_df.iterrows():
        sat_dict.update({index: sat["SATNAME"]})

    return sat_dict


def filter_cat_by_period(min_period, max_period, cat_df):
    cat_df = cat_df[cat_df["PERIOD"] > min_period]
    cat_df = cat_df[cat_df["PERIOD"] < max_period]
    return cat_df


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
    plt.rcParams["axes.prop_cycle"] = plt.cycler(color=["blue", "green", "red", "cyan", "magenta", "yellow",
                                                        "black", "purple", "pink", "brown", "orange", "teal",
                                                        "coral", "lightblue", "lime", "lavender", "turquoise",
                                                        "darkgreen", "tan", "salmon", "gold"])
    plt.ylabel("Elevation")
    ax = plt.gca()
    date_form = DateFormatter("%H:%M:%S")
    ax.xaxis.set_major_formatter(date_form)

    def draw_ang(self, df, sat_number):
        if len(df) < 5:
            return
        df_shadow = df[df["Ph"] == 0.0]
        df_shine = df[df["Ph"] != 0.0]
        if df_shine.size != 0:
            df_shine.plot(x="Time", y="Elev", grid=True, ax=self.ax, legend=False, xlabel="Time", marker="1",
                          linestyle="None")
        if df_shadow.size != 0:
            df_shadow.plot(x="Time", y="Elev", grid=True, ax=self.ax, legend=False, xlabel="Time", color="grey")
        middle_time = df.iloc[df["Elev"].idxmax()]["Time"]
        min_distance = str(df["Distance"].min() / 1000).split(".")[0]
        ann = sat_number + "(" + min_distance + ")"
        self.ax.annotate(ann, xy=(middle_time, df["Elev"].max()),
                         xytext=(-15, 15), textcoords="offset points",
                         arrowprops={"arrowstyle": "->"})

    def view(self, path):
        file_list = os.listdir(path)
        for file in file_list:
            sat_number = file.split(sep="_")[0]
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
            file_operations.write_ang(item[0], item[1], item[2])


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-10s) %(message)s', )



    conf = get_conf()
    # manager = EffectiveManager(conf)
    # ang_list = manager.get_ang_list()
    # for norad_id in ang_list.keys():
    #     ang = ang_list.get(norad_id)
    #     for a in ang:
    #         fn = manager.Ang.get_filename(a)
    #         d = manager.Ang.get_data(a)
    ang_dir = conf["angdirectory"]
    tle_dir = conf["tledirectory"]
    norad_cred = {"identity": conf["identity"], "password": conf["password"]}
    download = bool(conf["download"] == "True")
    period_filter = bool(conf["filter_by_period"] == "True")

    if download:
        downloader.download_tle(tle_dir, norad_cred)

    cat = file_operations.read_satcat()
    if period_filter:
        min_period = int(conf["min_period"])
        max_period = int(conf["max_period"])
        cat = filter_cat_by_period(min_period, max_period, cat)
    needed_sat = dict_from_df(cat)
    satellites = file_operations.read_tle(tle_dir, needed_sat)
    run_calc(conf, satellites)

    # if bool(conf["filter_by_sieve"] == "True"):  # Прореживание
    #     sieve = int(conf["sieve"])
    #     AngFilter.thin_out(ang_dir, sieve)

    app = AngViewer()  # Отображение
    app.view(ang_dir)
