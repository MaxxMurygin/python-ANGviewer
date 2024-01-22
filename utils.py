import linecache
import logging
import os
import re
from configparser import ConfigParser, NoSectionError, NoOptionError
from math import pi
import pandas as pd


def get_step_by_distance(dst):
    if dst <= 3000:
        return 1
    elif 3000 < dst <= 10000:
        return 2
    elif 10000 < dst <= 25000:
        return 8
    else:
        return 120


def correct_midnight(times):
    corr_times = []
    for time in times:
        if time > 86400:
            corr_times.append(time - 86400)
        else:
            corr_times.append(time)

    return corr_times


def rotate_by_pi(angles):
    rotated = []
    for angle in angles:
        if angle < pi:
            rotated.append(angle + pi)
        else:
            rotated.append(angle - pi)
    return rotated


def catalog_df_to_dict(cat_df):
    sat_dict = dict()
    for index, sat in cat_df.iterrows():
        sat_dict.update({index: sat["SATNAME"]})

    return sat_dict


def filter_catalog(config, cat_df):
    period_filter = bool(config["Filter"]["filter_by_period"] == "True")
    name_filter = bool(config["Filter"]["filter_by_name"] == "True")
    inclination_filter = bool(config["Filter"]["filter_by_inclination"] == "True")
    names_string = config["Filter"]["names_string"]
    if period_filter:
        cat_df = cat_df[cat_df["PERIOD"] > float(config["Filter"]["min_period"])]
        cat_df = cat_df[cat_df["PERIOD"] < float(config["Filter"]["max_period"])]
    if inclination_filter:
        cat_df = cat_df[cat_df["INCLINATION"] > float(config["Filter"]["min_inclination"])]
        cat_df = cat_df[cat_df["INCLINATION"] < float(config["Filter"]["max_inclination "])]
    if name_filter:
        cat_df["SATNAME"] = cat_df["SATNAME"].astype("string")
        cat_df = cat_df.loc[cat_df['SATNAME'].str.contains(names_string, flags=re.IGNORECASE)]
    return cat_df


def check_dirs(directory):
    full_path = os.path.join(os.getcwd(), directory)
    if not os.path.isdir(full_path):
        os.mkdir(full_path)
    return full_path


def get_config_from_file(filename='config.conf'):
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
        path = os.path.join(src_path, file)
        date = linecache.getline(path, 3).rstrip()
        time = linecache.getline(path, 4).rstrip()
        dt_int = int(date + time)
        df.loc[len(df)] = {"dt": dt_int, "file": file}
    df = df.sort_values(by="dt")
    counter = 0
    for index, row in df.iterrows():
        counter += 1
        if counter >= sieve:
            try:
                os.remove(os.path.join(src_path, row["file"]))
            except IOError:
                logging.error("<thin_out> Не могу удалить файл " + row["file"])
            counter = 0
