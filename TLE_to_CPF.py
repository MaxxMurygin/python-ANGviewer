import os
from datetime import timedelta, datetime

import sgp4.model
from sgp4.api import Satrec
from sgp4.api import jday
from sgp4.conveniences import sat_epoch_datetime
from skyfield.api import EarthSatellite, load
from skyfield.toposlib import wgs84


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
                # ts = load.timescale()
                # satellite = EarthSatellite(s, t, sat_name, ts)
                # print(satellite)
    return sats

def write_cpf(name, sat):
    eph = load('de421.bsp')
    ts = load.timescale()
    file_name = name + "_" + str(231123) + ".ang"
    file_name = os.path.join(os.getcwd(), "CPF", file_name)
    lat = 51.3439072
    lon = 82.1771946
    height = 371.081
    t = ts.now()
    aolc = wgs84.latlon(lat, lon, height)
    ts = load.timescale()
    satellite = EarthSatellite.from_satrec(sat, ts)
    satellite.name = name
    difference = satellite - aolc
    topocentric = difference.at(t)
    print(name)
    print(topocentric.position.km)
    alt, az, distance = topocentric.altaz()
    ra, dec, distance = topocentric.radec()
    sunlit = satellite.at(t).is_sunlit(eph)

    # if alt.degrees > 0:
    #     print('The ISS is above the horizon')
    print('Altitude:', alt)
    print('Azimuth:', az)
    print('Distance: {:.1f} km'.format(distance.km))
    print("RA: ", ra)
    print("DEC: ", dec)
    print('Sunlight:', sunlit)


def write_cpf_sgp4(name, sat):
    file_name = name + "_" + str(231123) + ".aolc"
    file_name = os.path.join(os.getcwd(), "CPF", file_name)
    # jd, fr = jday(2023, 11, 23, 0, 0, 0)
    dt_init = sat_epoch_datetime(sat)
    # mjd = int(sat.jdsatepoch - 2400000.5)
    h1 = "H1 CPF  2  SGF 2023 11 23  2  326 01 lageos1\n"
    h2 = "H2  7603901 1155    08820 2023 11 23  0  0  0 2023 11 23 23 55  0   300 1 1  0 0\n"
    h3 = "0 1\n"
    h4 = "H9\n"
    h = h1 + h2 + h3 + h4
    with open(file_name, 'w') as f:
        f.write(h)
        for i in range(0, 2000, 5):
            dt = dt_init + timedelta(minutes=i)
            jd, fr = jday(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
            mjd = int(jd - 2400000.5)
            # e, r, v = sat.sgp4(jd, fr)
            e, r, v = sat.sgp4_tsince(i)
            seconds = dt.hour * 3600 + dt.minute * 60 + dt.second
            # r1, v1 = sgp4.model.Satellite.propagate(sat, dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
            f.write("10 0 {} {:>13.6f}  0 {:>17.3f} {:>17.3f} {:>17.3f}\n".format(mjd, seconds, r[0] * 1000,
                                                                                  r[1] * 1000, r[2] * 1000))
        f.write("99")


def tle_to_cpf(file):
    satellites = read_tle(file)
    for name in satellites.keys():
        write_cpf(name, satellites[name])
