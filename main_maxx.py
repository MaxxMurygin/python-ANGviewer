import logging

import downloader
import file_operations
from manager import EffectiveManager
from utils import filter_cat_by_period, dict_from_df, run_calc, AngViewer

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-10s) %(message)s', )

    config_file = "config.conf"
    manager = EffectiveManager(config_file)
    conf = manager.get_conf()
    all_angs = manager.get_ang_dict()
    for norad_id in all_angs.keys():
        current_sat = all_angs.get(norad_id)
        print(norad_id)
        info = manager.get_sat_info(norad_id)
        for ang in current_sat.keys():
            d = current_sat.get(ang)
            print(ang, d)

    manager.delete_sat(12785)
    ang_dir = conf["Path"]["angdirectory"]
    tle_dir = conf["Path"]["tledirectory"]
    norad_cred = {"identity": conf["TLE"]["identity"], "password": conf["TLE"]["password"]}
    download = bool(conf["TLE"]["download"] == "True")
    period_filter = bool(conf["Filter"]["filter_by_period"] == "True")

    if download:
        downloader.download_tle(tle_dir, norad_cred)

    cat = file_operations.read_satcat()
    if period_filter:
        min_period = float(conf["Filter"]["min_period"])
        max_period = float(conf["Filter"]["max_period"])
        cat = filter_cat_by_period(min_period, max_period, cat)
    needed_sat = dict_from_df(cat)
    satellites = file_operations.read_tle(tle_dir, needed_sat)
    run_calc(conf, satellites)

    # if bool(conf["filter_by_sieve"] == "True"):  # Прореживание
    #     sieve = int(conf["sieve"])
    #     AngFilter.thin_out(ang_dir, sieve)

    app = AngViewer()  # Отображение
    app.view(ang_dir)