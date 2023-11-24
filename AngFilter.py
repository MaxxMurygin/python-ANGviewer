import os
import pandas as pd
from ang_rw import read_ang


def is_timely(hour):
    if (13 <= hour <= 15) or (1 <= hour <= 5):
        return True
    else:
        return False


def is_elevated(file, max_elevation):
    df = read_ang(file)
    if df["Um"].max() > max_elevation:
        return True
    else:
        return False


def base_filter(src_path, dst_path, max_elevation=60):
    for file in os.listdir(dst_path):
        os.remove(os.path.join(dst_path, file))
    for file in os.listdir(src_path):
        splited_filename = file.split("_")
        hour = int(splited_filename[2][0:2])
        if is_timely(hour):
            if is_elevated(os.path.join(src_path, file), max_elevation):
                os.system("copy " + os.path.join(src_path, file) + " " + os.path.join(dst_path, ""))


def thin_out(src_path, dst_path, sieve=10):
    for file in os.listdir(dst_path):
        os.remove(os.path.join(dst_path, file))
    df = pd.DataFrame(columns=["dt", "file"])
    for file in os.listdir(src_path):
        dt_str = file.split("_")[1] + file.split("_")[2][0:4]
        dt_int = int(dt_str)
        df.loc[len(df)] = {"dt": dt_int, "file": file}
    df = df.sort_values(by="dt")
    counter = 0
    for index, row in df.iterrows():
        if counter == sieve:
            counter = 0
            file_name = row["file"]
            os.system("copy " + os.path.join(src_path, file_name) + " " + os.path.join(dst_path, ""))
            continue
        counter += 1


def filter_by_distance(src_path, dst_path, min_distance=400000):
    for file in os.listdir(dst_path):
        os.remove(os.path.join(dst_path, file))
    for file in os.listdir(src_path):
        df = read_ang(os.path.join(src_path, file))
        if float(df["Distance"].min()) <= min_distance:
            os.system("copy " + os.path.join(src_path, file) + " " + os.path.join(dst_path, ""))
