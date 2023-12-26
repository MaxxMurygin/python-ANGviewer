import logging

from manager import EffectiveManager
from viewer import Viewer

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-10s) %(message)s', )

    config_file = "config.conf"
    manager = EffectiveManager(config_file)
    conf = manager.get_conf()
    ang_dir = conf["Path"]["angdirectory"]

    # manager.download_cat()
    # manager.download_tle()

    manager.calculate()

    app = Viewer()  # Отображение
    app.view(ang_dir)

    # all_angs = manager.get_ang_dict()
    # for norad_id in all_angs.keys():
    #     current_sat = all_angs.get(norad_id)
    #     # print(norad_id)
    #     info = manager.get_sat_info(norad_id)
    #     for ang in current_sat.keys():
    #         d = current_sat.get(ang)
    #         # print(ang, d)
    #
    # manager.delete_sat(41026)

    # if bool(conf["filter_by_sieve"] == "True"):  # Прореживание
    #     sieve = int(conf["sieve"])
    #     AngFilter.thin_out(ang_dir, sieve)
