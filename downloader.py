import logging
import os.path
from datetime import datetime, timedelta
import requests


def dl_http(url, file, norad_cred):
    login_norad_url = "https://www.space-track.org/ajaxauth/login"
    with requests.Session() as session:
        session.post(login_norad_url, data=norad_cred)
        r = session.get(url)
    if r.ok:
        with open(file, "wb") as outfile:
            outfile.write(r.content)
    else:
        logging.error("HTTP status : {0} ({1}) in {2}".format(r.status_code, r.reason, r.url))


def download_tle(tle_dir, norad_cred):
    # tle_file = os.path.join(os.getcwd(), tle_dir, "tle_test.tle")
    # url_custom = ("https://www.space-track.org/basicspacedata/query/class/gp/"
    #        "PERIOD/120--125/EPOCH/>now-30/orderby/NORAD_CAT_ID,EPOCH/format/3le")
    url_full_catalog = ("https://www.space-track.org/basicspacedata/query/class/gp/"
                        "EPOCH/%3Enow-30/orderby/NORAD_CAT_ID,EPOCH/format/3le")
    tle_full = os.path.join(os.getcwd(), tle_dir, "full.tle")
    url_geo = ("https://www.space-track.org/basicspacedata/query/class/gp/"
               "EPOCH/%3Enow-30/MEAN_MOTION/0.99--1.01/ECCENTRICITY/%3C0.01/OBJECT_TYPE/"
               "payload/orderby/NORAD_CAT_ID,EPOCH/format/3le")
    tle_geo = os.path.join(os.getcwd(), tle_dir, "geo.tle")
    url_meo = ("https://www.space-track.org/basicspacedata/query/class/gp/"
               "EPOCH/%3Enow-30/MEAN_MOTION/1.8--2.39/ECCENTRICITY/%3C0.25/OBJECT_TYPE/"
               "payload/orderby/NORAD_CAT_ID,EPOCH/format/3le")
    tle_meo = os.path.join(os.getcwd(), tle_dir, "meo.tle")
    url_leo = ("https://www.space-track.org/basicspacedata/query/class/gp/"
               "EPOCH/%3Enow-30/MEAN_MOTION/%3E11.25/ECCENTRICITY/%3C0.25/OBJECT_TYPE/"
               "payload/orderby/NORAD_CAT_ID,EPOCH/format/3le")
    tle_leo = os.path.join(os.getcwd(), tle_dir, "leo.tle")
    url_heo = ("https://www.space-track.org/basicspacedata/query/class/gp/"
               "EPOCH/%3Enow-30/ECCENTRICITY/%3E0.25/OBJECT_TYPE/payload/orderby/NORAD_CAT_ID,EPOCH/format/3le")
    tle_heo = os.path.join(os.getcwd(), tle_dir, "heo.tle")
    dl_http(url_full_catalog, tle_full, norad_cred)


def download_cat(norad_cred, cat_dir="CAT"):
    catalog_file = os.path.join(os.getcwd(), cat_dir, "catalog.csv")
    if os.path.isfile(catalog_file):
        cat_file_time = datetime.fromtimestamp(os.path.getmtime(catalog_file))
        if datetime.now() - cat_file_time < timedelta(days=30):
            return
    url = "https://www.space-track.org/basicspacedata/query/class/satcat/orderby/NORAD_CAT_ID%20asc/format/csv"
    dl_http(url, catalog_file, norad_cred)


def download_ephemeris(eph_file):
    url = "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/" + eph_file
    with requests.Session() as session:
        r = session.get(url)
    if r.ok:
        with open(eph_file, "wb") as outfile:
            outfile.write(r.content)
    else:
        logging.error("HTTP status : {0} ({1}) in {2}".format(r.status_code, r.reason, r.url))
