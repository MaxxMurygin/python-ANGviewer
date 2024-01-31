import logging
import os
from configparser import ConfigParser
from datetime import timedelta, datetime
from math import pi
import pandas as pd
from sgp4.model import Satrec
from skyfield.api import EarthSatellite, load


def read_catalog(satcat_file="catalog.csv"):
    file = os.path.join(os.getcwd(), "CAT", satcat_file)
    # col = ["INTLDES,NORAD_CAT_ID", "OBJECT_TYPE", "SATNAME", "COUNTRY", "LAUNCH", "SITE", "DECAY", "PERIOD",
    #        "INCLINATION", "APOGEE", "PERIGEE", "COMMENT", "COMMENTCODE", "RCSVALUE","RCS_SIZE", "FILE", "LAUNCH_YEAR",
    #        "LAUNCH_NUM", "LAUNCH_PIECE", "CURRENT", "OBJECT_NAME", "OBJECT_ID", "OBJECT_NUMBER"]
    cat_df = pd.read_csv(file, index_col=1)
    cat_df = cat_df.loc[cat_df["DECAY"].isna()]
    cat_df = cat_df.loc[cat_df["PERIOD"].notna()]
    cat_df["OBJECT_TYPE"] = cat_df["OBJECT_TYPE"].astype("string")
    return cat_df


def read_tle(tle_dir, tle_file, needed_sat):
    ts = load.timescale()
    satellites = dict()
    with open(os.path.join(tle_dir, tle_file), "r") as f:
        for line in f:
            line = line.rstrip()
            if line[0] == "1":
                s = line
            elif line[0] == "2":
                t = line
                try:
                    sat_number = int(s[2:7])
                except ValueError as e:
                    logging.error(str(e))
                    continue
                if sat_number not in needed_sat:
                    continue

                print(sat_number)
                satrec = Satrec.twoline2rv(s, t)
                sat = EarthSatellite.from_satrec(satrec, ts)
                sat.name = needed_sat.get(satrec.satnum)
                satellites[sat_number] = sat
    print(f"КА в выборке: {len(satellites)}")
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


def get_sat_number_from_ang(file):
    with open(file, "r") as f:
        first_line = f.readline()
    return int(first_line)


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


def write_ang(event, df, file):
    if df.empty:
        return
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


def write_config(conf, config_file="default.conf"):
    parser = ConfigParser(inline_comment_prefixes="#")
    parser.read_dict(conf)
    file = os.path.join(os.getcwd(), config_file)
    with open(file, 'w') as configfile:
        parser.write(configfile)
