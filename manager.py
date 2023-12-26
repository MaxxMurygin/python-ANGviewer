import multiprocessing
import os
from datetime import datetime

import pandas

import downloader
import file_operations
import utils
from tle_to_ang import AngCalculator
from file_operations import get_satnum_from_ang, read_ang, read_satcat, write_config

from utils import get_conf, filter_cat_by_period, dict_from_df


class EffectiveManager:
    def __init__(self, config_file="default.conf"):
        self.cat_df = pandas.DataFrame()
        self.ang_df = pandas.DataFrame()
        self.ang_list = list()
        self.ang_dict = dict()
        self.config = get_conf(config_file)
        self.catalog = self.__get_catalog("satcat.csv")
        self.tle_dir = self.config["Path"]["tledirectory"]
        self.ang_dir = self.config["Path"]["angdirectory"]
        self.status = ""

    def calculate(self):
        period_filter = bool(self.config["Filter"]["filter_by_period"] == "True")

        cat = file_operations.read_satcat()
        if period_filter:
            min_period = float(self.config["Filter"]["min_period"])
            max_period = float(self.config["Filter"]["max_period"])
            cat = filter_cat_by_period(min_period, max_period, cat)
        needed_sat = dict_from_df(cat)
        satellites = file_operations.read_tle(self.tle_dir, needed_sat)
        self.__run_calc(satellites)

    def get_ang_dict_with_data(self):
        self.status = "Чтение ang файлов"
        files = os.listdir(os.path.join(os.getcwd(), self.ang_dir))
        for file in files:
            full_path = os.path.join(os.getcwd(), self.ang_dir, file)
            sat_num = get_satnum_from_ang(full_path)
            df_ang = read_ang(full_path)
            single_ang = {file: df_ang}
            if sat_num in self.ang_dict:
                self.ang_dict[sat_num].update(single_ang)
            else:
                self.ang_dict[sat_num] = single_ang
        self.status = ""
        return self.ang_dict

    def get_ang_dict(self):
        self.status = "Чтение ang файлов"
        files = os.listdir(os.path.join(os.getcwd(), self.ang_dir))
        col = ["Time", "Distance", "Az", "Elev", "RA", "DEC", "Ph"]
        empty_df = pandas.DataFrame(columns=col)
        for file in files:
            full_path = os.path.join(os.getcwd(), self.ang_dir, file)
            satnum = get_satnum_from_ang(full_path)
            single_ang = {file: empty_df}
            if satnum in self.ang_dict:
                self.ang_dict[satnum].update(single_ang)
            else:
                self.ang_dict[satnum] = single_ang
        self.status = ""
        return self.ang_dict

    def download_tle(self):
        norad_cred = {"identity": self.config["TLE"]["identity"], "password": self.config["TLE"]["password"]}
        self.status = "Скачиваются TLE..."
        downloader.download_tle(self.tle_dir, norad_cred)
        self.status = ""

    def download_cat(self):
        cat_dir = self.config["Path"]["catdirectory"]
        norad_cred = {"identity": self.config["TLE"]["identity"], "password": self.config["TLE"]["password"]}
        self.status = "Скачивается каталог..."
        downloader.download_cat(norad_cred, cat_dir)
        self.status = ""

    def thin_out(self, sieve):
        self.status = "Идет прореживание..."
        utils.thin_out(self.config, sieve)
        self.status = ""

    def get_sat_info(self, norad_id):
        return self.catalog.loc[[norad_id]]

    def delete_sat(self, norad_id):
        try:
            angs = self.ang_dict.pop(norad_id)
            if angs:
                for ang in angs:
                    os.remove(os.path.join(os.getcwd(), self.config["Path"]["angdirectory"], ang))
        except KeyError:
            pass

    def get_conf(self):
        return self.config

    def set_conf(self, conf):
        self.config = conf

    def save_conf_to_file(self, conf_file):
        write_config(self.config, conf_file)

    def get_status(self):
        return self.status

    def __get_catalog(self, file):
        self.status = "Чтение каталога"
        cat = read_satcat(os.path.join(os.getcwd(), "CAT", file))
        self.status = ""
        return cat

    def __run_calc(self, satellites):
        threads_qty = int(self.config["System"]["threads"])
        splited_salellites = list()
        processes = list()
        ang_calculator_list = list()

        mp_manager = multiprocessing.Manager()
        lock = mp_manager.Lock()
        global_ang_list = mp_manager.list()

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
            ang_calculator_list.append(AngCalculator(self.config, sats))
        for ac in ang_calculator_list:
            process = multiprocessing.Process(target=ac.tle_to_ang, args=(global_ang_list, lock))
            processes.append(process)
            process.start()
        for _, process in enumerate(processes):
            process.join()
        perf = datetime.now() - perf_start
        print("Время расчета : {} sec".format(perf.seconds + perf.microseconds / 1000000))
        self.status = "Идет запись результатов расчета..."
        for items in global_ang_list:
            for item in items:
                file_operations.write_ang(item[0], item[1], item[2])
        self.status = ""
