import os
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
from file_operations import read_ang


class Viewer:
    plt.rcParams["figure.figsize"] = [18, 8]
    plt.rcParams["axes.prop_cycle"] = plt.cycler(color=["blue", "green", "red", "cyan", "magenta", "yellow",
                                                        "black", "purple", "pink", "brown", "orange", "teal",
                                                        "coral", "lightblue", "lime", "lavender", "turquoise",
                                                        "darkgreen", "tan", "salmon", "gold"])
    plt.ylabel("Elevation")
    ax = plt.gca()
    date_form = DateFormatter("%H:%M:%S")
    ax.xaxis.set_major_formatter(date_form)

    def draw_ang(self, df, sat_number):
        # if len(df) < 5:
        #     return
        # if sat_number == "28786":
        #     print()
        # print(df)
        df_shadow = df[df["Ph"] == 0.0]
        df_shine = df[df["Ph"] != 0.0]
        if df_shine.size != 0:
            df_shine.plot(x="Time", y="Elev", grid=True, ax=self.ax, legend=False, xlabel="Time", marker="1",
                          linestyle="None")
        if df_shadow.size != 0:
            df_shadow.plot(x="Time", y="Elev", grid=True, ax=self.ax, legend=False, xlabel="Time", color="grey")
        middle_time = df.iloc[df["Elev"].idxmax()]["Time"]
        min_distance = str(df["Distance"].min() / 1000).split(".")[0]
        ann = sat_number + "(" + min_distance + ")"
        self.ax.annotate(ann, xy=(middle_time, df["Elev"].max()),
                         xytext=(-15, 15), textcoords="offset points",
                         arrowprops={"arrowstyle": "->"})

    def view(self, path):
        file_list = os.listdir(path)
        for file in file_list:
            sat_number = file.split(sep="_")[0]
            # print(sat_number)
            self.draw_ang(read_ang(os.path.join(path, file)), sat_number)
        plt.show()
