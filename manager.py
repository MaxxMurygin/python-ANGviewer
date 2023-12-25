import os

import pandas

from file_operations import get_satnum_from_ang, read_ang, read_satcat

# from gui_ANGviewer.guiFormMainCode import guiFormMain,QtWidgets
# from PyQt5 import QtWidgets

# from utils import get_conf

class EffectiveManager:
    def __init__(self, config):
        self.cat_df = pandas.DataFrame()
        self.ang_df = pandas.DataFrame()
        self.ang_list = list()
        self.ang_dict = dict()
        self.config = config
        self.catalog = read_satcat()

    def get_ang_dict_with_data(self):
        files = os.listdir(os.path.join(os.getcwd(), "ANG"))
        for file in files:
            full_path = os.path.join(os.getcwd(), "ANG", file)
            satnum = get_satnum_from_ang(full_path)
            df_ang = read_ang(full_path)
            single_ang = {file: df_ang}
            if satnum in self.ang_dict:
                self.ang_dict[satnum].update(single_ang)
            else:
                self.ang_dict[satnum] = single_ang

        return self.ang_dict

    def get_ang_dict(self):
        files = os.listdir(os.path.join(os.getcwd(), "ANG"))
        col = ["Time", "Distance", "Az", "Elev", "RA", "DEC", "Ph"]
        empty_df = pandas.DataFrame(columns=col)
        for file in files:
            full_path = os.path.join(os.getcwd(), "ANG", file)
            satnum = get_satnum_from_ang(full_path)
            single_ang = {file: empty_df}
            if satnum in self.ang_dict:
                self.ang_dict[satnum].update(single_ang)
            else:
                self.ang_dict[satnum] = single_ang

        return self.ang_dict

    def get_sat_info(self, id):
        return self.catalog.loc[[id]]
