import os
from math import pi

import pandas as pd

import main


def is_timely(hour):
    if (13 <= hour <= 15) or (1 <= hour <= 5):
        return True
    else:
        return False


def is_elevated(file, max_elevation):
    col = ['Time', 'Distance', 'Az', 'Um', 'RA', 'DEC', 'Ph']
    df = pd.read_csv(file, sep=' ', names=col, index_col=None, skipinitialspace=True, skiprows=16)
    if df["Um"].max() > max_elevation:
        return True
    else:
        return False


def filter_1st(src_path, dst_path):
    max_elevation = 60 * pi / 180
    for file in os.listdir(dst_path):
        os.remove(os.path.join(dst_path, file))
    for file in os.listdir(src_path):
        splited_filename = file.split("_")
        hour = int(splited_filename[2][0:2])
        if is_timely(hour):
            if is_elevated(os.path.join(src_path, file), max_elevation):
                os.system("copy " + os.path.join(src_path, file) + " " + os.path.join(dst_path, ""))


def filter_2nd(src_path, dst_path):
    dropped_ang = 10
    for file in os.listdir(dst_path):
        os.remove(os.path.join(dst_path, file))
    df = pd.DataFrame(columns=["dt", "file"])
    for file in os.listdir(src_path):
        dt_str = file.split("_")[1] + file.split("_")[2][0:4]
        dt_int = int(dt_str)
        # dt = pd.to_datetime(dt_str, format="%Y%m%d%H%M%S")
        df.loc[len(df)] = {"dt": dt_int, "file": file}
    df = df.sort_values(by="dt")
    counter = 0
    for index, row in df.iterrows():
        if counter == dropped_ang:
            counter = 0
            file_name = row["file"]
            os.system("copy " + os.path.join(src_path, file_name) + " " + os.path.join(dst_path, ""))
            continue
        counter += 1


def filter_smart(src_path, dst_path):
    min_distance = 400000
    for file in os.listdir(dst_path):
        os.remove(os.path.join(dst_path, file))
    for file in os.listdir(src_path):
        df = main.read_ang(os.path.join(src_path, file))
        if float(df["Distance"].min()) <= min_distance:
            os.system("copy " + os.path.join(src_path, file) + " " + os.path.join(dst_path, ""))
