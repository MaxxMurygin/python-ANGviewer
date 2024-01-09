from builtins import type
from time import sleep

from PyQt5.Qt import *
from PyQt5.QtWidgets import *
# from PyQt5.QtCore import pyqtSlot
# import pyqtgraph as pg


import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.dates import DateFormatter,DayLocator,HourLocator,num2date
from matplotlib.ticker import MaxNLocator
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

import datetime

# plt.style.use('https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle')
# date_form = DateFormatter("%H:%M:%S")


import numpy as np

import collections

from manager import EffectiveManager
from gui_ANGviewer.guiFormMainAngView import *

import time


class guiFormMain(QtWidgets.QMainWindow, Ui_guiFormMain):
    def __init__(self, manader: EffectiveManager):
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.tableListKA.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tableListKA.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableKAInfo.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.tableKAInfo.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self.manager = manader
        self.all_angs = self.manager.get_ang_dict_with_data()
        self.ang_Line = dict() # Time, TimeShadow, polar, polarShadow
        self.ang_Line_Check = set()  # Time, TimeShadow, polar, polarShadow

        #Select
        self.selectAngGraph = set()
        self.listCheckAng = set()

        self.selectEffectsSel = [pe.Stroke(linewidth=5, foreground='magenta'), pe.Normal()]
        self.selectEffectsUnsel =[pe.Stroke(), pe.Normal()]


        InfLable = list(zip(["NUMBER", "NAME", "ID", "COUNTRY", "LAUNCH", "PERIOD"],
                             ["OBJECT_NUMBER", "OBJECT_NAME", "OBJECT_ID", "COUNTRY", "LAUNCH", "PERIOD"]))

        self.importantInf = dict(zip(range(7), InfLable))

        self.figGraphPolar, self.axGraphPolar = self.createGraphPolar()
        self.figGraphTime, self.axGraphTime = self.createGraphTime()

        self.tableListKA.itemSelectionChanged.connect(self.slotSelectKaList)
        self.buttResetSelection.released.connect(self.selectionReset)
        self.buttOnlyCheck.clicked.connect(self.showOnlyMarked)
        self.buttCalicANG.triggered.connect(self.callCalicANG)
        self.buttSetting.triggered.connect(self.callSettings)


        self.updateKADate()

    def updateKADate(self):

        if (bool(self.all_angs)):

            for norad_id in self.all_angs.keys():

                itemKa = QTreeWidgetItem(self.tableListKA)
                itemKa.setFlags(itemKa.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                itemKa.setCheckState(0, Qt.Unchecked)
                itemKa.setData(0, Qt.EditRole, norad_id)


                current_sat = self.all_angs.get(norad_id)  # Получить анги

                for ang in current_sat.keys():

                    if (len(current_sat)>1):

                        itemKa.setData(1, Qt.EditRole, "...")

                        itemAng = QTreeWidgetItem(itemKa)
                        itemAng.setFlags(itemAng.flags() | Qt.ItemIsUserCheckable)
                        itemAng.setCheckState(1, Qt.Unchecked)
                        itemAng.setData(1, Qt.EditRole, ang)

                        itemKa.addChild(itemAng)

                    else:
                        # print()
                        itemKa.setData(1, Qt.EditRole, ang)
                        # itemKa.setCheckState(1, Qt.Unchecked)
                        itemKa.setTextAlignment(1,Qt.AlignHCenter|Qt.AlignVCenter)

                    d = current_sat.get(ang)
                    # --------Отрисовка на графиках---------

                    df_shadow = d[d["Ph"] == 0.0]
                    df_shine = d[d["Ph"] != 0.0]

                    self.ang_Line[ang]=[
                        self.axGraphTime.plot(df_shine.Time.values, df_shine.Elev.values, linewidth= 2,)[0],
                        self.axGraphTime.plot(df_shadow.Time.values, df_shadow.Elev.values,
                                              linewidth=1, color="grey")[0],
                                              # linewidth= 1, color="grey", marker='.' , markersize = 1)[0],

                        self.axGraphPolar.plot(np.deg2rad(df_shine.Az.values), 90 - (df_shine.Elev.values),
                                                visible=False, linewidth=2)[0],
                        self.axGraphPolar.plot(np.deg2rad(df_shadow.Az.values), 90 - (df_shadow.Elev.values),
                                                visible=False, linewidth=1,  color="grey")[0]
                                                # visible = False, linewidth = 1, color = "grey", marker = '.', markersize = 1)[0]
                    ]
                    # ========================================
                # self.tableListKA.addTopLevelItem(itemKa);
        else:
            print("amgs_isEmpty")

    def createGraphPolar(self):

        # print(hasattr(self, 'figGraphTime'))
        if (hasattr(self, 'figGraphTime')):
            self.figGraphPolar.add_subplot(projection='polar')
        else:
            fig, ax = plt.subplots(facecolor="#e5e5e5", subplot_kw={'projection': 'polar'})
            ax.set_facecolor("#e5e5e5")

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

        fig, ax = plt.subplots(facecolor="#e5e5e5")
        ax.set_facecolor("#e5e5e5")

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
                                       'Date = ' + num2date(x).strftime("%H:%M:%S\n%d/%m/%Y")


        #TO DO includ limits for zoom



        self.layoutBottGrph.addWidget(FigureCanvas(fig))
        self.layoutBottGrph.itemAt(0).widget().setMinimumSize(QtCore.QSize(0, 300))
        toolbar = NavigationToolbar(fig.canvas, self)
        self.layoutBottGrph.addWidget(toolbar)


        return fig, ax

    def slotSelectKaList(self):
        start_time = time.time()

        newSelectAng = set()

        if not (self.selectAngGraph):#нет выбранных
            print()
            for keyLines in self.ang_Line_Check if bool(self.ang_Line_Check) else self.ang_Line.keys():
                self.ang_Line[keyLines][0].set(lw=2, alpha=0.2, path_effects=[pe.Stroke(), pe.Normal()])
                self.ang_Line[keyLines][1].set(lw=1, alpha=0.2, path_effects=[pe.Stroke(), pe.Normal()])

        self.tableKAInfo.clear()

        selectedColumns = self.tableListKA.selectedItems()

        # Заполнение информации
        if (len(selectedColumns)==1):

            idKA = (int(selectedColumns[0].data(0, Qt.EditRole)
                                if(selectedColumns[0].parent() is None)
                                else selectedColumns[0].parent().data(0, Qt.EditRole)))

            self.fillKaInfo(idKA)

        #===========================
        # Selected New
        for item in selectedColumns:

            if item.data(1, Qt.EditRole) in self.selectAngGraph:
                newSelectAng.add(item.data(1, Qt.EditRole))
                continue #Если КА уже отображён

            if (item.childCount()==0):
                newSelectAng.add(
                    self.selectGraph(item.data(1, Qt.EditRole))
                )

            else:
                for childIndex in range(item.childCount()):#проход по вложенным
                    newSelectAng.add(
                        self.selectGraph(item.child(childIndex).data(1, Qt.EditRole))
                    )

        # ===========================
        #   Unselected old
        for item in self.selectAngGraph - newSelectAng:

            self.selectAngGraph.discard(
                self.selectGraph(item,True)
            )


        self.selectAngGraph.update(newSelectAng)

        # print('repaint time: ', time.time() - start_time)


        self.figGraphPolar.canvas.draw()
        self.figGraphPolar.canvas.flush_events()
        self.figGraphTime.canvas.draw()
        self.figGraphTime.canvas.flush_events()
        self.repaint()

        # print('end time: ', time.time() - start_time)
        # print("\n")

    def fillKaInfo(self, idKa:int):
        # print("fillKaInfo")

        dataKA = self.manager.get_sat_info(idKa)

        for idInf, titleInf in self.importantInf.items():
            self.tableKAInfo.insertRow(idInf)

            itemLable = QTableWidgetItem()
            itemLable.setData(Qt.EditRole, titleInf[0])
            self.tableKAInfo.setItem(idInf, 0, itemLable)

            itemInf = QTableWidgetItem()
            itemInf.setData(Qt.EditRole, str(dataKA[titleInf[1]].values[0]))
            self.tableKAInfo.setItem(idInf, 1, itemInf)

    def selectGraph(self, angName:str, unselection=False)->str:

        self.ang_Line[angName][0].set(lw=3, zorder=2 if  (unselection)  else 3,
                                      alpha=0.1 if  (unselection)  else 1,
                                      path_effects=self.selectEffectsUnsel if
                                                      (unselection)  else
                                                      self.selectEffectsSel)
        self.ang_Line[angName][1].set(lw=2, zorder=2 if  (unselection)  else 3,
                                      alpha=0.1 if  (unselection)  else 1,
                                      path_effects=self.selectEffectsUnsel if
                                                      (unselection)  else
                                                      self.selectEffectsSel)
        self.ang_Line[angName][2].set_visible(not unselection)
        self.ang_Line[angName][3].set_visible(not unselection)

        return angName

    def selectionReset(self):

        for item in self.selectAngGraph:
            self.selectGraph(item,True)
        self.selectAngGraph.clear()

        size2 = len(self.selectAngGraph)==0
        if (size2):#нет выбранных
            for keyLines in self.ang_Line_Check if bool(self.ang_Line_Check) else self.ang_Line.keys():
                self.ang_Line[keyLines][0].set(lw=2, alpha=1, path_effects=[pe.Stroke(), pe.Normal()])
                self.ang_Line[keyLines][1].set(lw=1, alpha=1, path_effects=[pe.Stroke(), pe.Normal()])

        self.figGraphPolar.canvas.draw()
        self.figGraphTime.canvas.draw()

    def showOnlyMarked(self, checkState=True):


        for angSet in self.ang_Line.values():
            angSet[0].set_visible(not checkState)
            angSet[1].set_visible(not checkState)


        for itemKA in self.tableListKA.findItems("*",Qt.MatchRegExp|Qt.MatchWildcard,0):

            unvisible = (itemKA.checkState(0) == Qt.Unchecked
                                and itemKA.checkState(1) == Qt.Unchecked
                                         and checkState)
            itemKA.setHidden(unvisible)

            if (checkState and itemKA.childCount() == 0):
                angName = itemKA.data(1, Qt.EditRole)
                self.ang_Line[angName][0].set_visible(not unvisible)
                self.ang_Line[angName][1].set_visible(not unvisible)

            for childIndex in range(itemKA.childCount()):  # проход по вложенным
                unvisible = (itemKA.child(childIndex).checkState(1) != Qt.Checked
                                    and checkState)
                itemKA.child(childIndex).setHidden(unvisible)

                angName = itemKA.child(childIndex).data(1, Qt.EditRole)
                self.ang_Line[angName][0].set_visible(not unvisible)
                self.ang_Line[angName][1].set_visible(not unvisible)

        self.figGraphPolar.canvas.draw()
        self.figGraphTime.canvas.draw()



    def callCalicANG(self):
        print("вызов Расчёта")
        # self.timeKa.set_visible(not self.timeKa.get_visible())

    def callSettings(self):
        print("вызов настроек")
