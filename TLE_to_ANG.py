import multiprocessing
import os
from datetime import timedelta, datetime
from math import pi
import pandas
import pandas as pd
from skyfield.api import EarthSatellite, load
from skyfield.api import utc
from skyfield.toposlib import wgs84


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


def correct_midnight(times):
    corr_times = []
    for time in times:
        if time > 86400:
            corr_times.append(time - 86400)
        else:
            corr_times.append(time)

    return corr_times


class AngCalculator:
    ang_list = list()

    def __init__(self, conf, satellites):

        self.aolc = wgs84.latlon(float(conf["lat"]), float(conf["lon"]), float(conf["height"]))
        self.begin = (datetime.strptime(conf["tbegin"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=utc) -
                      timedelta(hours=3))
        self.end = (datetime.strptime(conf["tend"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=utc) -
                    timedelta(hours=3))
        self.tle_dir = conf["tledirectory"]
        self.ang_dir = conf["angdirectory"]
        self.filter_by_elevate = bool(conf["filter_by_elevation"] == "True")
        self.filter_by_distance = bool(conf["filter_by_distance"] == "True")
        self.filter_by_sunlite = bool(conf["filter_by_sunlite"] == "True")
        self.delete_existing = bool(conf["delete_existing"] == "True")
        self.min_distance = int(conf["min_distance"])
        self.max_distance = int(conf["max_distance"])
        self.angle_of_drop = int(conf["max_elevation"])
        self.sunlite = float(conf["sunlite"])
        self.satellites = satellites

    def find_events(self, sats):
        event_df = pd.DataFrame(columns=["SatNumber", "SatObject", "T0Event", "T1Event", "T2Event"])
        ts = load.timescale()
        ts_begin = ts.from_datetime(self.begin)
        ts_end = ts.from_datetime(self.end)
        for s in sats.values():
            try:
                sat = EarthSatellite.from_satrec(s, ts)
                difference = sat - self.aolc
                t_events, events = sat.find_events(self.aolc, ts_begin, ts_end, altitude_degrees=10.0)
                # if len(events) > 18:
                #     continue
                for i in range(0, len(t_events), 3):
                    times_list = [sat.model.satnum_str, sat, t_events[i], t_events[i + 1], t_events[i + 2]]
                    topocentric = difference.at(t_events[i + 1])
                    alt, az, distance = topocentric.altaz()
                    if self.filter_by_distance:
                        if not self.min_distance <= distance.km <= self.max_distance:
                            continue
                    if self.filter_by_elevate:
                        if alt.degrees >= self.angle_of_drop:
                            event_df.loc[len(event_df.index)] = times_list
                    else:
                        event_df.loc[len(event_df.index)] = times_list
            except:
                continue

        return event_df

    def calc_ang(self, event):
        arr = []
        eph = load("de440s.bsp")
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
        file_name = os.path.join(self.ang_dir, file_name)
        difference = satellite - self.aolc
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

        df = pandas.DataFrame(arr, columns=["Time", "Distance", "Az", "Elev", "RA", "DEC", "Ph"])
        df["Az"] = rotate(df["Az"])
        if df["Time"].max() > 86400:
            df["Time"] = correct_midnight(df["Time"])
        if self.filter_by_sunlite:
            if df["Ph"].mean() > self.sunlite:
                return [event, df, file_name]
            else:
                return 0
        return [event, df, file_name]

    def tle_to_ang(self, global_list, lock):
        local_list = list()
        proc_name = multiprocessing.current_process().name
        perf_start = datetime.now()
        events = self.find_events(self.satellites)
        perf = datetime.now() - perf_start
        print("*{}* Время расчета зон: {} sec".format(proc_name, perf.seconds + perf.microseconds / 1000000))
        if self.delete_existing:
            for file in os.listdir(self.ang_dir):
                os.remove(os.path.join(self.ang_dir, file))
        for _, event in events.iterrows():
            perf_start = datetime.now()
            item = self.calc_ang(event)
            if item != 0:
                local_list.append(item)
            perf = datetime.now() - perf_start
            print("*{}* Расчет прохода {}: {} sec".format(proc_name, event.iloc[0],
                                                          perf.seconds + perf.microseconds / 1000000))
        with lock:
            global_list.append(local_list)
