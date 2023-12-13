import os

import pandas

from file_operations import get_satnum_from_ang, read_ang


# from utils import get_conf


class EffectiveManager:
    def __init__(self, config):
        self.cat_df = pandas.DataFrame()
        self.ang_df = pandas.DataFrame()
        self.ang_list = list()
        self.ang_dict = dict()
        self.config = config

    class Ang:
        def __init__(self, filename, dataframe):
            self.filename = filename
            self.data = dataframe
        def get_filename(self):
            return self.filename

        def get_data(self):
            return self.data

    def get_ang_list_with_data(self):
        files = os.listdir(os.path.join(os.getcwd(), "ANG"))
        for file in files:
            full_path = os.path.join(os.getcwd(), "ANG", file)
            satnum = get_satnum_from_ang(full_path)
            df_ang = read_ang(full_path)
            single_ang = self.Ang(file, df_ang)
            if satnum in self.ang_dict:
                self.ang_dict[satnum].append(single_ang)
            else:
                self.ang_dict[satnum] = [single_ang]

        return self.ang_dict

    def get_ang_list(self):
        files = os.listdir(os.path.join(os.getcwd(), "ANG"))
        empty_df = pandas.DataFrame()
        for file in files:
            full_path = os.path.join(os.getcwd(), "ANG", file)
            satnum = get_satnum_from_ang(full_path)
            single_ang = self.Ang(file, empty_df)
            if satnum in self.ang_dict:
                self.ang_dict[satnum].append(single_ang)
            else:
                self.ang_dict[satnum] = [single_ang]

        return self.ang_dict
