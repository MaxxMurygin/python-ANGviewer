import logging
import multiprocessing
import os
from datetime import timedelta, datetime
from math import cos

# import pandas
import pandas as pd
from skyfield import almanac
from skyfield.api import load
from skyfield.api import utc
from skyfield.toposlib import wgs84
from utils import get_step_by_distance, rotate_by_pi, correct_midnight


# python -m jplephem excerpt 2023/1/1 2023/12/31 "https://naif.jpl.nasa.gov/pub/
# naif/generic_kernels/spk/planets/de440s.bsp" "de440s.bsp"

def events_to_list(t_events, events):
    t, e = list(), list()
    for i in range(0, len(events), 1):
        t.append(t_events[i])
        e.append(events[i])
    return t, e


def correct_borders(t_events, events, ts_begin, ts_end):
    if events[0] == 2:
        events = [1] + events
        t_events = [ts_begin] + t_events
    if events[0] == 1:
        events = [0] + events
        t_events = [ts_begin] + t_events
    if events[len(events) - 1] == 0:
        events.append(1)
        t_events.append(ts_end)
    if events[len(events) - 1] == 1:
        events.append(2)
        t_events.append(ts_end)

    return t_events, events


class Calculator:
    ang_list = list()

    def __init__(self, conf, satellites):

        self.aolc = wgs84.latlon(float(conf["Coordinates"]["lat"]), float(conf["Coordinates"]["lon"]),
                                 float(conf["Coordinates"]["height"]))
        self.begin = (datetime.strptime(conf["Basic"]["t_begin"], "%Y-%m-%d %H:%M:%S")
                      .replace(tzinfo=utc) - timedelta(hours=3))
        self.end = (datetime.strptime(conf["Basic"]["t_end"], "%Y-%m-%d %H:%M:%S")
                    .replace(tzinfo=utc) - timedelta(hours=3))
        self.tle_dir = conf["Path"]["tle_directory"]
        self.ang_dir = conf["Path"]["ang_directory"]
        self.eph_file = conf["Path"]["eph_file"]
        self.calculate_phase = bool(conf["Basic"]["calculate_phase"] == "True")
        self.filter_by_elevate = bool(conf["Filter"]["filter_by_elevation"] == "True")
        self.filter_by_distance = bool(conf["Filter"]["filter_by_distance"] == "True")
        self.filter_by_sunlite = bool(conf["Filter"]["filter_by_sunlite"] == "True")
        self.min_distance = int(conf["Filter"]["min_distance"])
        self.max_distance = int(conf["Filter"]["max_distance"])
        self.min_elevation = int(conf["Filter"]["min_elevation"])
        self.max_elevation = int(conf["Filter"]["max_elevation"])
        self.sunlite = float(conf["Filter"]["sunlite"])
        self.horizon = float(conf["Basic"]["horizon"])
        self.satellites = satellites

    def find_events(self, satellites):
        event_df = pd.DataFrame(columns=["SatNumber", "SatObject", "T0Event", "T1Event", "T2Event", "Step"])
        ts = load.timescale()
        ts_begin = ts.from_datetime(self.begin)
        ts_end = ts.from_datetime(self.end)
        for sat in satellites.values():
            try:
                difference = sat - self.aolc
                t_events, events = sat.find_events(self.aolc, ts_begin, ts_end, altitude_degrees=self.horizon)

                if len(events) == 0:
                    continue
                t_events, events = events_to_list(t_events, events)
                len_events = len(events)

                if events[0] != 0 or events[len_events - 1] != 2:
                    t_events, events = correct_borders(t_events, events, ts_begin, ts_end)

                for i in range(0, len(t_events), 3):
                    topocentric = difference.at(t_events[i + 1])
                    alt, az, distance = topocentric.altaz()
                    step = get_step_by_distance(distance.km)
                    times_list = [str(sat.model.satnum), sat, t_events[i], t_events[i + 1], t_events[i + 2], step]

                    if self.filter_by_distance:
                        if not self.min_distance <= distance.km <= self.max_distance:
                            continue
                    if self.filter_by_elevate:
                        if self.max_elevation >= alt.degrees >= self.min_elevation:
                            event_df.loc[len(event_df.index)] = times_list
                    else:
                        event_df.loc[len(event_df.index)] = times_list
            except Exception as e:
                logging.error(str(e) + f"(find_events) ID: {sat.model.satnum}")
                print(str(e) + f"(find_events) ID: {sat.model.satnum}")
                continue
        return event_df

    def calculate_ang_from_event(self, event):
        arr = []
        eph = load(self.eph_file)
        earth = eph['earth']
        sun = eph['sun']
        step = event.iloc[5]
        satellite = event.iloc[1]
        ts_begin = event.iloc[2]
        ts_end = event.iloc[4]
        dt_begin = datetime.strptime(ts_begin.utc_iso(), "%Y-%m-%dT%H:%M:%SZ")
        dt_end = datetime.strptime(ts_end.utc_iso(), "%Y-%m-%dT%H:%M:%SZ")

        t_current_in_sec = (dt_begin.hour * 3600 + dt_begin.minute * 60 + dt_begin.second +
                            dt_begin.microsecond / 1000000 + 10800)
        t_end_in_sec = t_current_in_sec + (dt_end - dt_begin).seconds
        file_name = event.iloc[0] + "_" + (dt_begin + timedelta(hours=3)).strftime("%d%H") + ".ang"
        file_name = os.path.join(self.ang_dir, file_name)
        difference = satellite - self.aolc

        ssb_aolc = earth + self.aolc
        ssb_satellite = earth + satellite

        ts_current = ts_begin
        while t_current_in_sec < t_end_in_sec:
            topocentric = difference.at(ts_current)
            alt, az, distance = topocentric.altaz()
            ra, dec, _ = topocentric.radec()
            if satellite.at(ts_current).is_sunlit(eph):
                if self.calculate_phase:

                    sun_position = ssb_satellite.at(ts_current).observe(sun)
                    aolc_position = ssb_satellite.at(ts_current).observe(ssb_aolc)
                    phase_angle = sun_position.separation_from(aolc_position).radians

                    # topocentric_sat_obs = ssb_satellite.at(ts_current).observe(ssb_obs).apparent()
                    # topocentric_sat_sun = ssb_satellite.at(ts_current).observe(sun).apparent()
                    # phase_angle = topocentric_sat_obs.separation_from(topocentric_sat_sun).radians
                    phase = cos(phase_angle / 2) ** 2
                else:
                    phase = 1.0
            else:
                phase = 0.0
            moment = [t_current_in_sec, distance.m, az.radians, alt.radians, ra.radians, dec.radians, phase]
            arr.append(moment)
            ts_current = ts_current + timedelta(seconds=step)
            t_current_in_sec = t_current_in_sec + step

        df = pd.DataFrame(arr, columns=["Time", "Distance", "Az", "Elev", "RA", "DEC", "Ph"])
        df["Az"] = rotate_by_pi(df["Az"])
        if df["Time"].max() > 86400:
            df["Time"] = correct_midnight(df["Time"])
        if self.filter_by_sunlite:
            percent_of_sunlit = len(df[df["Ph"] != 0.0]) / len(df)
            if percent_of_sunlit > self.sunlite:
                return [event, df, file_name]
            else:
                return 0
        return [event, df, file_name]

    def calculate(self, global_list, counter, lock):
        local_list = list()
        proc_name = multiprocessing.current_process().name
        perf_start = datetime.now()

        events = self.find_events(self.satellites)
        events_qty = len(events)
        perf = datetime.now() - perf_start
        print(f"*{proc_name}* Время расчета зон: {perf.seconds + perf.microseconds / 1000000} sec")
        count = 0
        for _, event in events.iterrows():
            count += 1
            perf_start = datetime.now()
            item = self.calculate_ang_from_event(event)
            if item != 0:
                local_list.append(item)

            counter[proc_name] = count / events_qty
            perf = datetime.now() - perf_start
            print(f"*{proc_name}* Расчет прохода {event.iloc[0]}: {perf.seconds + perf.microseconds / 1000000} sec")
        with lock:
            global_list.append(local_list)

    def get_sun_events(self):
        ts = load.timescale()
        eph = load(self.eph_file)
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        t0 = ts.utc(today.year, today.month, today.day, 5)
        t1 = ts.utc(tomorrow.year, tomorrow.month, tomorrow.day, 5)
        t, y = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(eph, self.aolc))
        return (datetime.strptime(t[0].utc_iso(), "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=3),
                datetime.strptime(t[1].utc_iso(), "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=3))
