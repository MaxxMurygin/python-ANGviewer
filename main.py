import os
from math import pi

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter


def read_ang(file):
    col = ['Time', 'Distance', 'Az', 'Um', 'RA', 'DEC', 'Ph']
    df = pd.read_csv(file, sep=' ', names=col, index_col=None, skipinitialspace=True, skiprows=16)
    splt = file.split("_")[1]
    df['Time'] = pd.to_datetime(splt, format="%Y%m%d") + pd.to_timedelta(df['Time'], unit='s')
    df['Az'] = df['Az'] * 180 / pi
    df['Um'] = df['Um'] * 180 / pi
    return df


class AngViewer:
    def draw_ang(self, ax, df, sat_number):
        df.plot(x='Time', y='Um', grid=True,  ax=ax, legend=False)
        middle_time = df["Time"].min() + (df["Time"].max() - df["Time"].min()) / 2
        ann = sat_number + "(" + str(df["Distance"].min())[0:3] + ")"
        ax.annotate(ann, xy=(middle_time, df["Um"].max()),
                    xytext=(-15, 15), textcoords='offset points',
                    arrowprops={'arrowstyle': '->'})

    def run(self, path):
        file_list = os.listdir(path)
        date_form = DateFormatter("%H:%M:%S")
        plt.rcParams["figure.figsize"] = [18, 8]
        plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['blue', 'green', 'red', 'cyan', 'magenta', 'yellow',
                                                            'black', 'purple', 'pink', 'brown', 'orange', 'teal',
                                                            'coral', 'lightblue', 'lime', 'lavender', 'turquoise',
                                                            'darkgreen', 'tan', 'salmon', 'gold'])
        plt.ylabel("Elevation")
        ax = plt.gca()
        ax.xaxis.set_major_formatter(date_form)

        for file in file_list:
            sat_number = file.split(sep='_')[0]
            self.draw_ang(ax, read_ang(os.path.join(path, file)), sat_number)
        plt.show()


if __name__ == '__main__':
    src_path = os.path.join(os.getcwd(), 'ANGsrc')
    first_stage_path = os.path.join(os.getcwd(), 'ANG1')
    second_stage_path = os.path.join(os.getcwd(), 'ANGfinal')
    smart_stage_path = os.path.join(os.getcwd(), 'ANGsmart')
    # AngFilter.filter_1st(src_path, first_stage_path)
    # AngFilter.filter_2nd(first_stage_path, second_stage_path)
    # AngFilter.filter_smart(src_path, smart_stage_path)
    app = AngViewer()
    app.run(smart_stage_path)
