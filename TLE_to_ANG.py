import os
from datetime import timedelta, datetime

import pandas
import pandas as pd
from skyfield.api import EarthSatellite, load

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


def corrent_midnight(times):
    corr_times = []
    for time in times:
        if time > 86400:
            corr_times.append(time - 86400)
        else:
            corr_times.append(time)

    return corr_times


def find_events(dt_begin, dt_end, sats, aolc):
    angle_of_drop = 50
    event_df = pd.DataFrame(columns=['SatNElevber', 'SatObject', 'T0Event', 'T1Event', 'T2Event'])
    ts = load.timescale()
    ts_begin = ts.from_datetime(dt_begin)
    ts_end = ts.from_datetime(dt_end)
    for s in sats.values():
        try:
            sat = EarthSatellite.from_satrec(s, ts)
            difference = sat - aolc
            t_events, events = sat.find_events(aolc, ts_begin, ts_end, altitude_degrees=10.0)
            if len(events) > 9:
                continue
            print("Считаем проходы для ", sat.model.satnElev_str)
            for i in range(0, len(t_events), 3):
                times_list = [sat.model.satnElev_str, sat, t_events[i], t_events[i + 1], t_events[i + 2]]
                topocentric = difference.at(t_events[i + 1])
                alt, az, distance = topocentric.altaz()
                if alt.degrees >= angle_of_drop:
                    event_df.loc[len(event_df.index)] = times_list
        except:
            continue

    return event_df


def calc_ang(event, aolc):
    arr = []
    eph = load('de440s.bsp')
    step = 1
    satellite = event.iloc[1]
    ts_begin = event.iloc[2]
    ts_end = event.iloc[4]
    dt_begin = datetime.strptime(ts_begin.utc_iso(), "%Y-%m-%dT%H:%M:%SZ")
    dt_end = datetime.strptime(ts_end.utc_iso(), "%Y-%m-%dT%H:%M:%SZ")

    t_current_in_sec = (dt_begin.hour * 3600 + dt_begin.minute * 60 + dt_begin.second +
                      dt_begin.microsecond / 1000000 + 10800)
    t_end_in_sec = (dt_end.hour * 3600 + dt_end.minute * 60 + dt_end.second +
                    dt_end.microsecond / 1000000 + 10800)
    file_name = event.iloc[0] + "_" + (dt_begin + timedelta(hours=3)).strftime("%d%H") + ".ang"
    file_name = os.path.join(os.getcwd(), "ANG", file_name)
    difference = satellite - aolc
    ts_current = ts_begin

    while t_current_in_sec < t_end_in_sec:
        topocentric = difference.at(ts_current)
        alt, az, distance = topocentric.altaz()
        ra, dec, _ = topocentric.radec()
        if satellite.at(ts_current).is_sunlit(eph):
            sunlit = 1.0
        else:
            sunlit = 0.0
        moment = [t_current_in_sec, distance.m, az.radians, alt.radians, ra.radians, dec.radians, sunlit]
        arr.append(moment)
        ts_current = ts_current + timedelta(seconds=step)
        t_current_in_sec = t_current_in_sec + step

    df = pandas.DataFrame(arr, columns=['Time', 'Distance', 'Az', 'Elev', 'RA', 'DEC', 'Ph'])
    df["Az"] = rotate(df["Az"])
    if df["Time"].max() > 86400:
        df["Time"] = corrent_midnight(df["Time"])
    if df["Ph"].mean() > 0.7:
        ang_rw.write_ang(event, df, file_name)


def tle_to_ang(file, begin, end):
    lat = 51.3439072
    lon = 82.1771946
    height = 371.081
    aolc = wgs84.latlon(lat, lon, height)
    begin = begin - timedelta(hours=3)
    end = end - timedelta(hours=3)
    perf_start = datetime.now()
    events = find_events(begin, end, ang_rw.read_tle(file), aolc)
    perf = datetime.now() - perf_start
    print("Время расчета зон: {} sec".format(perf.seconds + perf.microseconds / 1000000))
    for index, event in events.iterrows():
        perf_start = datetime.now()
        calc_ang(event, aolc)
        perf = datetime.now() - perf_start
        print("Расчет прохода {}:{} sec".format(event.iloc[0], perf.seconds + perf.microseconds / 1000000))
