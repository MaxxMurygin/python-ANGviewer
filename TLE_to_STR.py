import os
from datetime import timedelta

from sgp4.api import Satrec
from sgp4.conveniences import sat_epoch_datetime
from sgp4.api import jday


def write_str(s, t):
    sat_number = int(t[1:7])
    file_name = str(sat_number) + ".str"
    full_file_name = os.path.join(os.getcwd(), "STR", file_name)
    satellite = Satrec.twoline2rv(s, t)
    e, r, v = satellite.sgp4(satellite.jdsatepoch, satellite.jdsatepochF)
    dt = sat_epoch_datetime(satellite) + timedelta(hours=3)
    date = dt.date().strftime("%d%m%y")
    time = dt.time().strftime("%H%M%S") + "." + "{:.3f}".format(dt.microsecond / 1000000).split(".")[1]
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute = dt.minute
    second = dt.second
    microsecond = dt.microsecond
    # jd, fr = jday(year, month, day, hour, minute, second)  # I pick an epoch (close to the TLE's)
    # e, r, v = satellite.sgp4(jd, fr)  # e = error, r = position vector, v = speed vector
    with open(full_file_name, 'w') as f:
        f.write("1" + "\n")
        f.write(str(sat_number) + "\n")
        f.write("1" + "\n")
        f.write(str(date) + "\n")
        f.write(str(time) + "\n")
        f.write(str(v[0] * 1000) + "\n")
        f.write(str(v[1] * 1000) + "\n")
        f.write(str(v[2] * 1000) + "\n")
        f.write(str(r[0] * 1000) + "\n")
        f.write(str(r[1] * 1000) + "\n")
        f.write(str(r[2] * 1000) + "\n")
        f.write("0.0" + "\n")
        f.write("0.0" + "\n")
        f.write("0.0" + "\n")
        f.write("0.0" + "\n")
        f.write("0.0" + "\n")
        f.write("0.0" + "\n")
        f.write("0.0" + "\n")
        f.write("0.0" + "\n")
        f.write("0" + "\n")
    print(sat_number, dt, e, r, v)


def tle_to_str(file):
    with open(file, 'r') as file:
        for line in file:
            line = line.rstrip()
            if line[0] == "0":
                sat_name = line[2:]
            elif line[0] == "1":
                s = line
            elif line[0] == "2":
                t = line
                write_str(s, t)

    # s = '1 28446U 04041A   19002.21559949 -.00000090  00000-0  00000+0 0  9998'
    # t = '2 28446   0.0198  37.5572 0002596 225.6438 170.9111  1.00271812 52071'
    # jd, fr = jday(2019, 1, 1, 11, 59, 33)  # I pick an epoch (close to the TLE's)
    # e, r, v = satellite.sgp4(jd, fr)  # e = error, r = position vector, v = speed vector
