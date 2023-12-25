from builtins import type

from PyQt5.Qt import *
from PyQt5.QtWidgets import *
# from PyQt5.QtCore import pyqtSlot
# import pyqtgraph as pg


import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

# plt.style.use('https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle')

import numpy as np

import collections

from manager import EffectiveManager
from gui_ANGviewer.guiFormMainAngView import *


class guiFormMain(QtWidgets.QMainWindow, Ui_guiFormMain):
    def __init__(self, manader: EffectiveManager):
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.manager = manader
        self.all_angs = self.manager.get_ang_dict_with_data()

        self.figGraphPolar,self.axGraphPolar = self.createGraphPolar()
        self.figGraphTime,self.axGraphTime = self.createGraphTime()

        Az = self.all_angs[480]['480_1119.ang'].Az.values
        Elev =  self.all_angs[480]['480_1119.ang'].Elev.values
        time = self.all_angs[480]['480_1119.ang'].Time.values
        self.axGraphPolar.plot(np.deg2rad(Az), 90 - Elev, linestyle='', marker='.')
        self.timeKa, =  self.axGraphTime.plot(time,Elev)


        self.buttCalicANG.triggered.connect(self.callCalicANG)
        self.buttSetting.triggered.connect(self.callSettings)

        self.updateKADate()

    def updateKADate(self):
        if (bool(self.all_angs)):
            # print("amgs_isNotEmpty")
            row = 0
            for norad_id in self.all_angs.keys():
                # print(norad_id)
                # ------Заполнение таблици КА--------
                self.tableListKA.insertRow(row)

                dateItem = QTableWidgetItem()
                dateItem.setData(Qt.EditRole, norad_id)
                self.tableListKA.setItem(row, 0, dateItem)
                row += 1
                # ===================================
                current_sat = self.all_angs.get(norad_id) #Получить анги
                for ang in current_sat.keys(): #num Ang
                    d = current_sat.get(ang)
                    # print (d.size())

                    Az = d.Az.values
                    Elev = d.Elev.values
                    time = d.Time.values
                    self.axGraphPolar.plot(np.deg2rad(Az), 90 - Elev, linestyle='', marker='.')
                    self.timeKa, = self.axGraphTime.plot(time, Elev)


                    # print(ang, d)

        else:
            print("amgs_isEmpty")
        # print("amgs_isEmpty")
        # print(type((self.manager1.)))

    def createGraphPolar(self):

        # print(hasattr(self, 'figGraphTime'))
        if (hasattr(self, 'figGraphTime')):
            self.figGraphPolar.add_subplot(projection='polar')
        else:
            fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

        ax.set_theta_zero_location("N")  # Начало север
        ax.set_theta_direction(-1)  # Отразить

        ax.set_rlim(bottom=0, top=90, emit=1)  # Установите пределы обзора по радиальной оси
        ax.set_yticks(np.arange(0, 91, 15))  #Сетка

        ax.set_yticklabels(ax.get_yticks()[::-1])
        ax.set_rlabel_position(120)

        if (True):
            labels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            compass = [n / float(len(labels)) * 2 * np.pi for n in range(len(labels))]
            compass += compass[:1]
            plt.xticks(compass[:-1], labels)

        self.layoutGraphPolar.addWidget(FigureCanvas(fig))
        self.layoutGraphPolar.itemAt(0).widget().setMinimumSize(QtCore.QSize(300, 300))
        # self.layoutGraphPolar.itemAt(0).widget().setMinimumSize(QtCore.QSize(1, 1))
        print("rePaintGraphPolar")
        return fig, ax

    def createGraphTime(self):

        fig, ax = plt.subplots()

        ax.set_ylabel("Elevation")
        ax.set_yticks(np.arange(0, 91, 10))
        ax.set_ylim(bottom=0, top=90, emit=1)

        ax.set_xlabel("Time")

        ax.grid(True)

        self.layoutBottGrph.addWidget(FigureCanvas(fig))
        self.layoutBottGrph.itemAt(0).widget().setMinimumSize(QtCore.QSize(0, 300))
        toolbar = NavigationToolbar(fig.canvas, self)
        self.layoutBottGrph.addWidget(toolbar)

        # date_form = DateFormatter("%H:%M:%S")
        # ax.xaxis.set_major_formatter(date_form)

        return fig, ax


    def callCalicANG(self):

        self.timeKa.set_visible(not self.timeKa.get_visible())
        self.figGraphTime.canvas.draw()
        self.repaint()

        print("вызов Расчёта")

    def callSettings(self):
        print("вызов настроек")

    # def test(self):
    #     # print("aksjdasjd")
    #     self.tableListKA.setItem(1,1,QTableWidgetItem(str("akjshdkhas")))
    #     # self.tableListKA.item(1,1).set('aksjghdakjhd')
