import os

import pandas

from utils import get_conf


class EffectiveManager:
    def __init__(self, config: str):
        cat_df = pandas.DataFrame()
        ang_df = pandas.DataFrame()
        ang_list = list()
        ang_dict = dict()
        config = get_conf(config)

    def get_ang_list(self):

        return os.listdir(os.path.join(os.getcwd(), "ANG"))

    def get_ang_list_with_data(self):
        return dict()
