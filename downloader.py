import logging
import os.path
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
    cat_file = os.path.join(os.getcwd(), tle_dir, "tle_test.tle")
    url = ("https://www.space-track.org/basicspacedata/query/class/gp/"
           "PERIOD/120--125/EPOCH/>now-30/orderby/NORAD_CAT_ID,EPOCH/format/3le")
    dl_http(url, cat_file, norad_cred)
