from builtins import type

from PyQt5.Qt import *
from PyQt5.QtWidgets import *
# from PyQt5.QtCore import pyqtSlot
# import pyqtgraph as pg


import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter,DayLocator,HourLocator,num2date
from matplotlib.ticker import MaxNLocator
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

import datetime

plt.style.use('https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle')
# date_form = DateFormatter("%H:%M:%S")


import numpy as np

import collections

from manager import EffectiveManager
from gui_ANGviewer.guiFormMainAngView import *


class guiFormMain(QtWidgets.QMainWindow, Ui_guiFormMain):
    def __init__(self, manader: EffectiveManager):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.tableListKA.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tableListKA.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tableListKA.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        self.manager = manader
        self.all_angs = self.manager.get_ang_dict_with_data()
        self.ang_Line = dict()
        self.visibleAngPolar = list()

        self.figGraphPolar,self.axGraphPolar = self.createGraphPolar()
        self.figGraphTime,self.axGraphTime = self.createGraphTime()

        self.tableListKA.itemSelectionChanged.connect(self.slotSelectKaList)
        self.buttCalicANG.triggered.connect(self.callCalicANG)
        self.buttSetting.triggered.connect(self.callSettings)


        self.updateKADate()

    def updateKADate(self):
        if (bool(self.all_angs)):

            row = 0

            for norad_id in self.all_angs.keys():

                self.tableListKA.insertRow(row)
                # ------Заполнение таблици КА--------

                itemCheckBox = QCheckBox()
                self.tableListKA.setCellWidget(row, 0, itemCheckBox)
                # self.tableListKA.cellWidget(row,0).setAlignment(Qt.AlignCenter)
                # self.tableListKA.item(row, 0).setAlignment(Qt.AlignCenter)


                itemKa = QTableWidgetItem()
                itemKa.setData(Qt.EditRole, norad_id)
                self.tableListKA.setItem(row, 1, itemKa)

                current_sat = self.all_angs.get(norad_id)  # Получить анги

                itemCauntAng = QTableWidgetItem()
                itemCauntAng.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                itemCauntAng.setData(Qt.EditRole, len(current_sat))
                self.tableListKA.setItem(row, 2, itemCauntAng)

                itemAng = QComboBox()if(len(current_sat)>1)else QTableWidgetItem()

                for ang in current_sat.keys():

                    if (len(current_sat)>1):

                        itemBox = QStandardItem()
                        itemBox.setText(ang)
                        itemBox.setCheckable(True)

                        itemAng.model().appendRow(itemBox)
                        itemAng.setLayoutDirection(QtCore.Qt.RightToLeft)
                    else:
                        print()
                        itemAng.setData(Qt.EditRole, ang)

                    d = current_sat.get(ang)
                    # --------Отрисовка на графиках---------

                    df_shadow = d[d["Ph"] == 0.0]
                    df_shine = d[d["Ph"] != 0.0]

                    self.ang_Line[ang]=[
                        self.axGraphTime.plot(df_shine.Time.values, df_shine.Elev.values, linewidth= 1)[0],
                        self.axGraphTime.plot(df_shadow.Time.values, df_shadow.Elev.values, linewidth= 1, color="grey")[0],
                        self.axGraphPolar.plot(np.deg2rad(df_shine.Az.values), 90 - (df_shine.Elev.values),
                                                visible=False, linewidth= 1)[0],
                        self.axGraphPolar.plot(np.deg2rad(df_shadow.Az.values), 90 - (df_shadow.Elev.values),
                                                visible=False, linewidth= 1, color="grey")[0]
                    ]
                    # ========================================

                    # self.axGraphPolar.plot(np.deg2rad(d.Az.values), 90 - d.Elev.values, linestyle='', marker='.')
                    # self.axGraphTime.plot(d.Time.values, d.Elev.values)

                if (len(current_sat) > 1):
                    self.tableListKA.setCellWidget(row, 3, itemAng)
                else:
                    print()
                    self.tableListKA.setItem(row, 3, itemAng)

                row += 1
                # ===================================
        else:
            print("amgs_isEmpty")


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

        ax.set_yticklabels([])

        # ax.set_yticklabels(ax.get_yticks()[::-1])
        # ax.set_rlabel_position(120)

        if (True):
            labels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            compass = [n / float(len(labels)) * 2 * np.pi for n in range(len(labels))]
            compass += compass[:1]
            plt.xticks(compass[:-1], labels)

        self.layoutGraphPolar.addWidget(FigureCanvas(fig))
        self.layoutGraphPolar.itemAt(0).widget().setMinimumSize(QtCore.QSize(300, 300))
        print("rePaintGraphPolar")
        return fig, ax

    def createGraphTime(self):

        fig, ax = plt.subplots()

        ax.set_ylabel("Elevation")
        ax.set_yticks(np.arange(0, 91, 10))
        ax.set_ylim(bottom=0, top=90, emit=1)

        ax.xaxis.set_major_locator(DayLocator())
        ax.xaxis.set_major_formatter(DateFormatter('%d/%m/%y'))
        ax.tick_params(axis='x', which='major',
                       labelsize=16, pad=12,
                       colors='r',
                       grid_color='r')

        # hLocator = HourLocator()
        # hLocator.MAXTICKS=10000
        ax.xaxis.set_minor_locator(HourLocator())
        ax.xaxis.set_minor_formatter(DateFormatter("%H:%M:%S"))
        ax.tick_params(axis='x', which='minor',
                       labelsize=8)

        ax.grid(True)
        ax.grid(axis='x', which='minor',linewidth = 1.5)


        ax.format_coord = lambda x, y: 'Elevation = ' + format(y, '1.2f') + ', ' + \
                                       'Date = ' + num2date(x).strftime("%H:%M:%S\n%m/%d/%Y")


        #TO DO includ limits for zoom



        self.layoutBottGrph.addWidget(FigureCanvas(fig))
        self.layoutBottGrph.itemAt(0).widget().setMinimumSize(QtCore.QSize(0, 300))
        toolbar = NavigationToolbar(fig.canvas, self)
        self.layoutBottGrph.addWidget(toolbar)


        return fig, ax

    def slotSelectKaList(self):

        #Спрятать старые
        for ang in self.visibleAngPolar:
            self.ang_Line[ang][2].set_visible(False)
            self.ang_Line[ang][3].set_visible(False)

        selectColumns = self.tableListKA.selectionModel().selectedRows(3)

        if (len(selectColumns)==1):
            self.fillKaInfo(self.tableListKA.item(selectColumns[0].row(), 1).data(Qt.EditRole))
            # t = self.fillKaInfo(int(201))
            print(1)


        for item in selectColumns:
            # print(int(itemCauntAng.data(Qt.EditRole)))
            # print(self.tableListKA.item(item.row(),2).data(Qt.EditRole))

            if (self.tableListKA.item(item.row(),2).data(Qt.EditRole)>1):

                for InemBox in self.tableListKA.cellWidget(item.row(), 3).model().findItems("",Qt.MatchContains):
                    self.visibleAngPolar.append(str(InemBox.text()))
                    self.ang_Line[InemBox.text()][2].set_visible(True)
                    self.ang_Line[InemBox.text()][3].set_visible(True)

            else:
                self.visibleAngPolar.append(str(item.data()))
                self.ang_Line[item.data()][2].set_visible(True)
                self.ang_Line[item.data()][3].set_visible(True)

        print("slotSelectKaList")
        self.figGraphPolar.canvas.draw()
        self.repaint()
    # self.tableListKA.cellWidget(item.row(), 0).setChecked(True)

    def fillKaInfo(self, idKa:int):
        x=self.manager.get_sat_info(int(idKa))





        print("fillKaInfo")


    def callCalicANG(self):

        # self.timeKa.set_visible(not self.timeKa.get_visible())

        print("вызов Расчёта")

    def callSettings(self):
        print("вызов настроек")
