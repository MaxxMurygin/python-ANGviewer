import os
from configparser import ConfigParser
from datetime import datetime
from skyfield.api import utc
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter

from TLE_to_ANG import AngCalculator
from ang_rw import read_ang
import AngFilter


def check_dirs(directory):
    full_path = os.path.join(os.getcwd(), directory)
    if not os.path.isdir(full_path):
        os.mkdir(full_path)
    return full_path


def get_conf(filename='config.conf'):
    parser = ConfigParser(inline_comment_prefixes="#")
    parser.read(os.path.join(os.getcwd(), filename))
    conf = {}
    try:
        for section in parser.sections():
            items = parser.items(section)
            conf.update(items)
    except Exception as err:
        # logging.error(str(err))
        return
    return conf


class AngViewer:
    plt.rcParams["figure.figsize"] = [18, 8]
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['blue', 'green', 'red', 'cyan', 'magenta', 'yellow',
                                                        'black', 'purple', 'pink', 'brown', 'orange', 'teal',
                                                        'coral', 'lightblue', 'lime', 'lavender', 'turquoise',
                                                        'darkgreen', 'tan', 'salmon', 'gold'])
    plt.ylabel("Elevation")
    ax = plt.gca()
    date_form = DateFormatter("%H:%M:%S")
    ax.xaxis.set_major_formatter(date_form)

    def draw_ang(self, df, sat_number):
        df_shadow = df[df['Ph'] == 0.0]
        df_shine = df[df['Ph'] != 0.0]
        if df_shine.size != 0:
            df_shine.plot(x='Time', y='Elev', grid=True, ax=self.ax, legend=False, xlabel="Time", marker="1")
        if df_shadow.size != 0:
            df_shadow.plot(x='Time', y='Elev', grid=True, ax=self.ax, legend=False, xlabel="Time", color="grey")
        middle_time = df.iloc[df["Elev"].idxmax()]["Time"]
        min_distance = str(df["Distance"].min() / 1000).split(".")[0]
        ann = sat_number + "(" + min_distance + ")"
        self.ax.annotate(ann, xy=(middle_time, df["Elev"].max()),
                         xytext=(-15, 15), textcoords='offset points',
                         arrowprops={'arrowstyle': '->'})

    def run(self, path):
        file_list = os.listdir(path)
        for file in file_list:
            sat_nElevber = file.split(sep='_')[0]
            self.draw_ang(read_ang(os.path.join(path, file)), sat_nElevber)
        plt.show()


if __name__ == '__main__':
    tle_file = os.path.join(check_dirs("TLE"))
    ang_path = check_dirs('ANG')
    conf = get_conf()

    calc = AngCalculator(conf)
    calc.tle_to_ang()

    app = AngViewer()
    app.run(ang_path)
