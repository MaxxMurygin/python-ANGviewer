import logging
import os
from configparser import ConfigParser, NoSectionError, NoOptionError

import pandas as pd


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
            conf[section] = {}
            for key, val in parser.items(section):
                conf[section][key] = val
    except (NoSectionError, NoOptionError) as e:
        logging.error(str(e))
        return
    return conf


def thin_out(src_path, sieve=10):
    df = pd.DataFrame(columns=["dt", "file"])
    for file in os.listdir(src_path):
        dt_str = file.split("_")[1].replace(".ang", "")
        dt_int = int(dt_str)
        df.loc[len(df)] = {"dt": dt_int, "file": file}
    df = df.sort_values(by="dt")
    counter = 0
    for index, row in df.iterrows():
        if counter == sieve:
            counter = 0
            continue
        else:
            os.remove(os.path.join(src_path, row["file"]))
        counter += 1
