from math import pi
import pandas as pd
from sgp4.model import Satrec


def get_date_from_ang(file):
    date = ""
    counter = 0
    file = open(file, 'r')
    for line in file:
        if counter == 2:
            date = line.strip("\n")
            break
        counter += 1
    return date


def read_ang(file):
    midnight_index = 0
    col = ['Time', 'Distance', 'Az', 'Um', 'RA', 'DEC', 'Ph']
    df = pd.read_csv(file, sep=' ', names=col, index_col=None, skipinitialspace=True, skiprows=16)
    date_and_time = get_date_from_ang(file)
    over_midnight = False
    if df['Time'].max() - df['Time'].min() > 85000:
        over_midnight = True
    if not over_midnight:
        df['Time'] = pd.to_datetime(date_and_time, format="%d%m%Y") + pd.to_timedelta(df['Time'], unit='s')
    else:
        for index, row in df.iterrows():
            if df.iloc[index]['Time'] > df.iloc[int(index) + 1]['Time']:
                midnight_index = int(index) + 1
                break
        df1 = df.iloc[:midnight_index, :]
        df2 = df.iloc[midnight_index:, :]
        df2.loc[:, "Time"] = df2.loc[:, "Time"] + 86400
        df = pd.concat([df1, df2])
        df['Time'] = pd.to_datetime(date_and_time, format="%d%m%Y") + pd.to_timedelta(df['Time'], unit='s')
    df['Az'] = df['Az'] * 180 / pi
    df['Um'] = df['Um'] * 180 / pi
    return df


def write_ang(arr, file):
    with open(file, "w") as f:
        for row in arr:
            f.write("{:>20.11f}{:>24.9f}{:>24.16f}{:>24.16f}{:>24.16f}"
                    "{:>24.16f}{:>11.3f}\n".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))


def read_tle(file):
    sats = dict()
    with open(file, 'r') as file:
        for line in file:
            line = line.rstrip()
            if line[0] == "0":
                sat_name = line[2:].lower().replace(" ", "")
            elif line[0] == "1":
                s = line
            elif line[0] == "2":
                t = line
                satellite = Satrec.twoline2rv(s, t)
                sats[sat_name] = satellite
    return sats
