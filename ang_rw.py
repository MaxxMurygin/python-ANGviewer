import os
from math import pi
import pandas as pd
from datetime import timedelta, datetime
from sgp4.model import Satrec


def read_tle(tle_dir):
    satellites = dict()
    for file in os.listdir(tle_dir):
        with open(os.path.join(tle_dir, file), "r") as f:
            for line in f:
                line = line.rstrip()
                if line[0] == "1":
                    s = line
                    sat_number = s[2:7]
                elif line[0] == "2":
                    t = line
                    satellite = Satrec.twoline2rv(s, t)
                    satellites[sat_number] = satellite
    return satellites


def make_header(sat_number, dt_begin, dt_end, row_qty):
    begin = dt_begin.strftime("%d%m%Y%H%M%S")
    end = dt_end.strftime("%d%m%Y%H%M%S")
    header = ("        {0}\n"
              "          0\n"
              "{1}\n"
              "{2}\n"
              "{3}\n"
              "{4}\n"
              "{5}\n"
              "                 0.0\n"
              "                 0.0\n"
              "                 0.0\n"
              "                 0.0\n"
              "                 0.0\n"
              "                 0.0\n"
              "                 0.0\n"
              "      22122\n"
              "       {6}\n").format(sat_number, begin[0:8], begin[8:],
                                     end[0:8], end[8:], begin[0:8], row_qty)
    return header


def get_date_from_ang(file):
    date = ""
    counter = 0
    file = open(file, "r")
    for line in file:
        if counter == 2:
            date = line.strip("\n")
            break
        counter += 1
    return date


def read_ang(file):
    midnight_index = 0
    col = ["Time", "Distance", "Az", "Elev", "RA", "DEC", "Ph"]
    df = pd.read_csv(file, sep=" ", names=col, index_col=None, skipinitialspace=True, skiprows=16)
    date_and_time = get_date_from_ang(file)
    over_midnight = False
    if df["Time"].max() - df["Time"].min() > 85000:
        over_midnight = True
    if not over_midnight:
        df["Time"] = pd.to_datetime(date_and_time, format="%d%m%Y") + pd.to_timedelta(df["Time"], unit="s")
    else:
        for index, row in df.iterrows():
            if df.iloc[index]["Time"] > df.iloc[int(index) + 1]["Time"]:
                midnight_index = int(index) + 1
                break
        df1 = df.iloc[:midnight_index, :]
        df2 = df.iloc[midnight_index:, :]
        df2.loc[:, "Time"] = df2.loc[:, "Time"] + 86400
        df = pd.concat([df1, df2])
        df["Time"] = pd.to_datetime(date_and_time, format="%d%m%Y") + pd.to_timedelta(df["Time"], unit="s")
    df["Az"] = df["Az"] * 180 / pi
    df["Elev"] = df["Elev"] * 180 / pi
    return df


# class Writer:

def write_ang(event, df, file):
    sat_number = event.iloc[0]
    dt_begin = datetime.strptime(event.iloc[2].utc_iso(), "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=3)
    dt_end = datetime.strptime(event.iloc[4].utc_iso(), "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=3)
    row_qty = len(df)
    with open(file, "w") as f:
        f.write(make_header(sat_number, dt_begin, dt_end, row_qty))
        for _, row in df.iterrows():
            f.write("{:>20.11f}{:>24.9f}{:>24.16f}{:>24.16f}{:>24.16f}{:>24.16f}"
                    "{:>11.3f}\n".format(row.iloc[0], row.iloc[1], row.iloc[2],
                                         row.iloc[3], row.iloc[4], row.iloc[5], row.iloc[6]))
