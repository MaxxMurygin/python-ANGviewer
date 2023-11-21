import os
from math import pi

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter

import AngFilter


def get_date_from_ang(file):
    date = ""
    counter = 0
    file = open(file, 'r')
    for line in file:
        if counter == 2:
            date = line.strip("\n")
            break
        counter += 1
    return date


def read_ang(file):
    midnight_index = 0
    col = ['Time', 'Distance', 'Az', 'Um', 'RA', 'DEC', 'Ph']
    df = pd.read_csv(file, sep=' ', names=col, index_col=None, skipinitialspace=True, skiprows=16)
    date_and_time = get_date_from_ang(file)
    over_midnight = False
    if df['Time'].max() - df['Time'].min() > 85000:
        over_midnight = True
    if not over_midnight:
        df['Time'] = pd.to_datetime(date_and_time, format="%d%m%Y") + pd.to_timedelta(df['Time'], unit='s')
    else:
        for index, row in df.iterrows():
            if df.iloc[index]['Time'] > df.iloc[int(index) + 1]['Time']:
                midnight_index = int(index) + 1
                break
        df1 = df.iloc[:midnight_index, :]
        df2 = df.iloc[midnight_index:, :]
        df2.loc[:, "Time"] = df2.loc[:, "Time"] + 86400
        df = pd.concat([df1, df2])
        df['Time'] = pd.to_datetime(date_and_time, format="%d%m%Y") + pd.to_timedelta(df['Time'], unit='s')
    df['Az'] = df['Az'] * 180 / pi
    df['Um'] = df['Um'] * 180 / pi
    return df


def check_dirs(directory):
    full_path = os.path.join(os.getcwd(), directory)
    if not os.path.isdir(full_path):
        os.mkdir(full_path)
    return full_path


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
    # ax.set_title("Περάσματα δορυφόρων")

    def draw_ang(self, df, sat_number):
        df.plot(x='Time', y='Um', grid=True, ax=self.ax, legend=False, xlabel="Time")
        middle_time = df["Time"].min() + (df["Time"].max() - df["Time"].min()) / 2
        min_distance = str(df["Distance"].min() / 1000).split(".")[0]
        ann = sat_number + "(" + min_distance + ")"
        self.ax.annotate(ann, xy=(middle_time, df["Um"].max()),
                         xytext=(-15, 15), textcoords='offset points',
                         arrowprops={'arrowstyle': '->'})

    def run(self, path):
        file_list = os.listdir(path)
        for file in file_list:
            sat_number = file.split(sep='_')[0]
            self.draw_ang(read_ang(os.path.join(path, file)), sat_number)
        plt.show()


if __name__ == '__main__':
    src_path = check_dirs('ANGsrc')
    first_stage_path = check_dirs('ANG1')
    second_stage_path = check_dirs('ANGfinal')
    smart_stage_path = check_dirs('ANGsmart')
    # AngFilter.filter_1st(src_path, first_stage_path)
    # AngFilter.filter_2nd(first_stage_path, second_stage_path)
    # AngFilter.filter_by_distance(src_path, smart_stage_path)
    app = AngViewer()
    app.run(src_path)
