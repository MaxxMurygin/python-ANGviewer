import os
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
from AngReader import read_ang
import AngFilter


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
    src_path = check_dirs('ANGsrc')                 # Источник
    first_stage_path = check_dirs('ANG1')           # Базовый фильтр
    second_stage_path = check_dirs('ANGfinal')      # Прореживание
    smart_stage_path = check_dirs('ANGsmart')       # Фильтр по минимальной дальности

    max_elevation = 60                              # Фильтр по УМ
    sieve = 10                                      # Прореживание

    AngFilter.base_filter(src_path, first_stage_path)
    AngFilter.thin_out(first_stage_path, second_stage_path, sieve)
    AngFilter.filter_by_distance(second_stage_path, smart_stage_path, max_elevation)
    app = AngViewer()
    app.run(second_stage_path)
