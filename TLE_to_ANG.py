import os
from datetime import timedelta, datetime

import pandas
from skyfield.api import EarthSatellite, load
from skyfield.api import utc
from skyfield.toposlib import wgs84
from math import pi
import ang_rw


# python -m jplephem excerpt 2023/1/1 2023/12/31 "https://naif.jpl.nasa.gov/pub/
# naif/generic_kernels/spk/planets/de440s.bsp" "de440s.bsp"

def rotate(angles):
    rotated = []
    for angle in angles:
        if angle < pi:
            rotated.append(angle + pi)
        else:
            rotated.append(angle - pi)
    return rotated

def calc_ang(name, sat):
    slow_step = 1
    fast_step = 10
    horizon = 10
    arr = []
    eph = load('de440s.bsp')
    ts = load.timescale()
    dt_begin = datetime(2023, 11, 24, 3, 0, 0, 0, tzinfo=utc)
    t_begin = ts.from_datetime(dt_begin)
    t_begin_in_sec = dt_begin.hour * 3600 + dt_begin.minute * 60 + dt_begin.second + dt_begin.microsecond / 1000000
    dt_end = datetime(2023, 11, 24, 4, 30, 0, 0, tzinfo=utc)
    t_end = ts.from_datetime(dt_end)
    iter_count = int((dt_end - dt_begin).seconds / slow_step)
    file_name = sat.satnum_str + "_" + str(231123) + ".ang"
    file_name = os.path.join(os.getcwd(), "CPF", file_name)
    lat = 51.3439072
    lon = 82.1771946
    height = 371.081
    aolc = wgs84.latlon(lat, lon, height)
    ts = load.timescale()
    satellite = EarthSatellite.from_satrec(sat, ts)
    satellite.name = name
    difference = satellite - aolc
    t_current = t_begin
    t_current_in_sec = t_begin_in_sec + 10800
    perf_start = datetime.now()
    i = 0
    t_events, events = satellite.find_events(aolc, t_begin, t_end, altitude_degrees=10.0)
    for ti, event in zip(t_events, events):
        if event == 0:
            beg = ti
        elif event == 1:
            culm = ti

    while i < iter_count:
        topocentric = difference.at(t_current)
        alt, az, distance = topocentric.altaz()
        ra, dec, distance = topocentric.radec()
        if alt.degrees > horizon:
            if satellite.at(t_current).is_sunlit(eph):
                sunlit = 1.0
            else:
                sunlit = 0.0
            moment = [t_current_in_sec, distance.m, az.radians, alt.radians, ra.radians, dec.radians, sunlit]
            arr.append(moment)
            i += slow_step
            t_current = t_current + timedelta(seconds=slow_step)
            t_current_in_sec = t_current_in_sec + slow_step
        else:
            i += fast_step
            t_current = t_current + timedelta(seconds=fast_step)
            t_current_in_sec = t_current_in_sec + fast_step
    df = pandas.DataFrame(arr, columns=['Time', 'Distance', 'Az', 'Um', 'RA', 'DEC', 'Ph'])
    df["Az"] = rotate(df["Az"])
    perf = datetime.now() - perf_start
    print("{} sec".format(perf.seconds + perf.microseconds / 1000000))
    ang_rw.write_ang(arr, file_name)


def tle_to_ang(file):
    satellites = ang_rw.read_tle(file)
    for name in satellites.keys():
        calc_ang(name, satellites[name])
