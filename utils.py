import logging
import os
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


def filter_catalog_by_period(min_period, max_period, cat_df):
    cat_df = cat_df[cat_df["PERIOD"] > min_period]
    cat_df = cat_df[cat_df["PERIOD"] < max_period]
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
