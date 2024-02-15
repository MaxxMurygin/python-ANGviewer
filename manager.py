import copy
import logging
import multiprocessing
import os
import shutil
from datetime import datetime
from time import sleep

import pandas
import downloader
import file_operations
import utils
from calculator import Calculator
from file_operations import get_sat_number_from_ang, read_ang, read_catalog, write_config
from utils import get_config_from_file, filter_catalog, catalog_df_to_dict


class EffectiveManager:
    def __init__(self, config_file="default.conf"):
        self.cat_df = pandas.DataFrame()
        self.ang_df = pandas.DataFrame()
        self.ang_list = list()
        self.ang_dict = dict()
        self.status = ""
        self.config = get_config_from_file(config_file)
        self.__init_vars()
        self.check_files()
        print("Files checked")
        self.catalog = self.__get_catalog()
        print("Cat get")
        self.mp_manager = multiprocessing.Manager()
        print("MP manager created")
        self.lock = self.mp_manager.Lock()
        self.global_ang_list = self.mp_manager.list()
        self.global_counter = self.mp_manager.dict()
        self.global_commander = ""
        print("Init complete")

    def calculate(self, tle_file):
        work_cat = self.catalog
        if bool(self.config["Filter"]["filter_enabled"] == "True"):
            work_cat = filter_catalog(self.config, self.catalog)
        needed_sat = catalog_df_to_dict(work_cat)
        satellites = file_operations.read_tle(self.tle_dir, tle_file, needed_sat)
        self.status = "Идет расчет"
        self.__run_calc(satellites)
        self.status = ""

    def get_ang_dict_with_data(self):
        self.status = "Чтение ang файлов"
        if len(self.ang_dict) != 0:
            self.ang_dict.clear()
        files = os.listdir(os.path.join(os.getcwd(), self.ang_dir))
        for file in files:
            full_path = os.path.join(os.getcwd(), self.ang_dir, file)
            sat_num = get_sat_number_from_ang(full_path)
            df_ang = read_ang(full_path)
            if not df_ang.empty:
                single_ang = {file: df_ang}
                if sat_num in self.ang_dict:
                    self.ang_dict[sat_num].update(single_ang)
                else:
                    self.ang_dict[sat_num] = single_ang
        self.status = ""
        return self.ang_dict

    def get_ang_dict(self):
        self.status = "Чтение ang файлов"
        if len(self.ang_dict) != 0:
            self.ang_dict.clear()
        files = os.listdir(os.path.join(os.getcwd(), self.ang_dir))
        col = ["Time", "Distance", "Az", "Elev", "RA", "DEC", "Ph"]
        empty_df = pandas.DataFrame(columns=col)
        for file in files:
            full_path = os.path.join(os.getcwd(), self.ang_dir, file)
            sat_number = get_sat_number_from_ang(full_path)
            single_ang = {file: empty_df}
            if sat_number in self.ang_dict:
                self.ang_dict[sat_number].update(single_ang)
            else:
                self.ang_dict[sat_number] = single_ang
        self.status = ""
        return self.ang_dict

    def download_tle(self):
        norad_cred = {"identity": self.config["TLE"]["identity"], "password": self.config["TLE"]["password"]}
        self.status = "Скачиваются TLE..."
        downloader.download_tle(self.tle_dir, norad_cred)
        self.status = ""

    def download_cat(self):
        cat_dir = self.config["Path"]["cat_directory"]
        norad_cred = {"identity": self.config["TLE"]["identity"], "password": self.config["TLE"]["password"]}
        self.status = "Скачивается каталог..."
        downloader.download_cat(norad_cred, cat_dir)
        self.status = ""

    def download_eph(self):
        self.status = "Скачиваются эфемериды..."
        downloader.download_ephemeris(self.eph_file)
        self.status = ""

    def thin_out(self, sieve):
        self.status = "Идет прореживание..."
        utils.thin_out(self.ang_dir, sieve)
        self.status = ""

    def get_sat_info(self, norad_id):
        if norad_id in self.catalog.index:
            return self.catalog.loc[[norad_id]]
        else:
            self.catalog.loc[norad_id] = ["1957-001A", "PAYLOAD", "FAKE", "AOLC", "1957-10-04", "TTMTR", "", "100.00",
                                          "66.66", "999", "999", "", "4", "0", "LARGE", "1", "1957",
                                          "1", "A", "Y", "FAKE SATELLITE", "1957-001A", f"{norad_id}"]
            return self.catalog.loc[[norad_id]]

    def get_full_tle_date(self):
        path = os.path.join(os.getcwd(), self.tle_dir, self.full_tle_file)
        m_time = datetime.fromtimestamp(os.path.getmtime(path))
        return m_time

    def get_catalog_date(self):
        path = os.path.join(os.getcwd(), self.cat_dir, self.cat_file)
        m_time = datetime.fromtimestamp(os.path.getmtime(path))
        return m_time

    def delete_sat(self, norad_id):
        try:
            angs = self.ang_dict.pop(norad_id)
            if angs:
                for ang in angs:
                    os.remove(os.path.join(os.getcwd(), self.ang_dir, ang))
        except KeyError:
            logging.error(f"<delete_sat> Не могу удалить КА № {norad_id}")
            pass

    def delete_all(self):
        files = os.listdir(utils.check_dirs(self.ang_dir))
        for file in files:
            try:
                os.remove(os.path.join(self.ang_dir, file))
            except IOError:
                logging.error("<thin_out> Не могу удалить файл " + file)
        self.ang_dict.clear()

    def get_config(self):
        return copy.deepcopy(self.config)

    def set_config(self, conf):
        self.config = conf
        self.__init_vars()
        self.check_files()

    def save_config_to_file(self, config_file):
        write_config(self.config, config_file)

    def open_config_from_file(self, config_file):
        self.config = get_config_from_file(config_file)

    def get_status(self):
        return self.status

    def terminate(self):
        self.global_commander = "STOP"

    def copy_ang_to_dst(self, dst):
        self.status = "Идет копирование..."
        try:
            shutil.copytree(os.path.join(os.getcwd(), self.ang_dir), dst, dirs_exist_ok=True)
        except IOError as e:
            logging.error(e)
        self.status = ""

    def get_sunrise_sunset(self):
        """
        Функция возвращает время заката солнца на текущие сутки (по системному времени) и время восхода на следующие сутки
        :return:
        [datetime.datetime, datetime.datetime]
        """
        return Calculator(self.config, None).get_sun_events()

    def check_files(self):
        if not os.path.isdir(self.ang_dir):
            os.mkdir(os.path.join(os.getcwd(), self.ang_dir))
        if not os.path.isdir(self.cat_dir):
            os.mkdir(os.path.join(os.getcwd(), self.cat_dir))
        if not os.path.isdir(self.tle_dir):
            os.mkdir(os.path.join(os.getcwd(), self.tle_dir))
        path_tle = os.path.join(os.getcwd(), self.tle_dir, self.full_tle_file)
        path_cat = os.path.join(os.getcwd(), self.cat_dir, self.cat_file)
        path_eph = os.path.join(os.getcwd(), self.eph_file)
        if not os.path.isfile(path_tle):
            self.download_tle()
        if not os.path.isfile(path_cat):
            self.download_cat()
        if not os.path.isfile(path_eph):
            self.download_eph()

    def __init_vars(self):
        self.tle_dir = self.config["Path"]["tle_directory"]
        self.ang_dir = self.config["Path"]["ang_directory"]
        self.cat_dir = self.config["Path"]["cat_directory"]
        self.cat_file = self.config["Path"]["cat_file"]
        self.full_tle_file = self.config["TLE"]["default_file"]
        self.eph_file = self.config["Path"]["eph_file"]
        self.delete_existing = bool(self.config["Path"]["delete_existing"] == "True")

    def __get_catalog(self):
        self.status = "Чтение каталога"
        cat_path = os.path.join(os.getcwd(), self.cat_dir, self.cat_file)
        if not os.path.isfile(cat_path):
            self.download_cat()
        cat = read_catalog(cat_path)
        self.status = ""
        return cat

    def __run_calc(self, satellites):
        threads_qty = int(self.config["System"]["threads"])
        splited_satellites = list()
        processes = list()
        calculator_list = list()
        self.global_commander = ""
        self.global_counter.clear()
        self.global_ang_list[:] = []
        if len(satellites) < threads_qty:
            for i in range(0, len(satellites)):
                splited_satellites.append(dict())
        else:
            for i in range(0, threads_qty):
                splited_satellites.append(dict())
        i = 0
        for key, value in satellites.items():
            splited_satellites[i].update({key: value})
            if i == len(splited_satellites) - 1:
                i = 0
            else:
                i += 1
        perf_start = datetime.now()
        for satellite in splited_satellites:
            calculator_list.append(Calculator(self.config, satellite))
        for ac in calculator_list:
            process = multiprocessing.Process(target=ac.calculate, args=(self.global_ang_list,
                                                                         self.global_counter, self.lock))
            processes.append(process)
            process.start()
        is_alive = True
        while is_alive:
            is_alive = False
            for proc in processes:
                if self.global_commander == "STOP":
                    if proc.is_alive():
                        proc.terminate()
                if proc.is_alive():
                    is_alive = True
            with self.lock:
                self.status = f"{round((sum(self.global_counter.values()) / threads_qty * 100), 2)}% выполнено"
            print(self.status)
            sleep(2)
        perf = datetime.now() - perf_start
        calc_time_str = f"Время расчета : {round((perf.seconds + perf.microseconds / 1000000), 2)} сек"
        print(calc_time_str)
        self.status = calc_time_str + ". Идет запись результатов расчета..."
        for items in self.global_ang_list:
            for item in items:
                file_operations.write_ang(item[0], item[1], item[2])
        # self.status = f"Время расчета : {perf.seconds + perf.microseconds / 1000000} sec"
