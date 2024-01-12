import os
from builtins import type, print
from time import sleep

from PyQt5.Qt import *
from PyQt5.QtWidgets import *
# from PyQt5.QtCore import pyqtSlot
# import pyqtgraph as pg


import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.dates import DateFormatter, DayLocator, HourLocator, num2date
from matplotlib.ticker import MaxNLocator
from numpy.distutils.fcompiler import str2bool

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


class GuiFormMain(QtWidgets.QMainWindow, Ui_guiFormMain):
    def __init__(self, manader: EffectiveManager):
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.manager = manader
# ----------------------------Setting--------------------------------
        self.actionSettings = ActionSettings(self)

        self.SettPathButtTLE.clicked.connect(self.actionSettings.setPathTLE)
        self.SettPathButtCAT.clicked.connect(self.actionSettings.setPathCAT)
        self.SettPathButtANG.clicked.connect(self.actionSettings.setPathANG)
        self.SettButtCancel.clicked.connect(self.actionSettings.clickedCancel)
        self.SettButtSeve.clicked.connect(self.actionSettings.clickedSave)
# ----------------------------Calic---------------------------------

        self.actionSettings = ActionCalic(self)

# ----------------------------View---------------------------------
        self.actionView = ActionView(self)

        self.tableListKA.itemSelectionChanged.connect(self.actionView.slotSelectKaList)
        self.buttResetSelection.released.connect(self.actionView.selectionReset)
        self.buttOnlyCheck.clicked.connect(self.actionView.showOnlyMarked)



    def callCalicANG(self):
        print("вызов Расчёта")
        # self.timeKa.set_visible(not self.timeKa.get_visible())

    def callSettings(self):
        print("вызов настроек")



class ActionSettings():
    def __init__(self, mainForm: GuiFormMain):
        print("__init__ actionSettings")
        self.mainForm = mainForm
        self.currentConfig = self.mainForm.manager.get_config()  # To Do Перенести в Main

        if not (self.currentConfig):
            print("Упс конфига нифига")
            return

        self.configViewUpdate(self.currentConfig)

    def configViewUpdate(self, currentConfig, firstReading=False):

        # if firstReading:
        #     self.mainForm.SettSystemStreamEdit.setValue(int(currentConfig["System"]['threads']))
        # elif (self.mainForm.SettSystemStreamEdit.value()
        #       != int(self.currentConfig["System"]['threads'])):
        #     self.mainForm.SettSystemStreamEdit.setStyleSheet("background-color: rgb(255, 0, 0);")
        # else:
        #     self.mainForm.SettSystemStreamEdit.setValue(int(currentConfig["System"]['threads']))
        #     self.mainForm.SettSystemStreamEdit.setStyleSheet("")

        self.mainForm.SettSystemStreamEdit.setValue(int(currentConfig["System"]['threads']))

        self.mainForm.SettCoordSpinBoxLat.setValue(float(currentConfig['Coordinates']['lat']))
        self.mainForm.SettCoordSpinBoxLon.setValue(float(currentConfig['Coordinates']['lon']))
        self.mainForm.SettCoordSpinBoxHeight.setValue(float(currentConfig['Coordinates']['height']))
        self.mainForm.SettCoordSpinBoxHorizont.setValue(int(currentConfig['Basic']['horizon']))

        self.mainForm.SettPathEditTLE.setText(currentConfig['Path']['tle_directory'])
        self.mainForm.SettPathEditCAT.setText(currentConfig['Path']['cat_directory'])
        # self.mainForm.SettPathEditFilterConf.setText(currentConfig['Path'][])
        self.mainForm.SettPathEditANG.setText(currentConfig['Path']['ang_directory'])
        self.mainForm.SettPathCheckANG.setChecked(str2bool(currentConfig['Path']['delete_existing']))

        self.mainForm.SettTLELoadBox.setChecked(str2bool(currentConfig['TLE']['download']))
        self.mainForm.SettTLELoadLog.setText(currentConfig['TLE']['identity'])
        self.mainForm.SettTLELoadPass.setText(currentConfig['TLE']['password'])

    def __getPathDir__(self) -> str:

        cwd = os.getcwd()
        Path = QFileDialog.getExistingDirectory(self.mainForm,
                                                "Open Directory",
                                                cwd,
                                                QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog
                                                )
        if (Path.find(cwd) < 0):
            return "Err"

        return Path.replace(cwd, '')[1:]

    def checkApplyConfig(self):

        self.mainForm.SettSystemStreamEdit.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                         (self.mainForm.SettSystemStreamEdit.value() != int(
                                                             self.currentConfig["System"]['threads']))
                                                         else "")

        self.mainForm.SettCoordSpinBoxLat.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                        (self.mainForm.SettCoordSpinBoxLat.value() != float(
                                                            self.currentConfig['Coordinates']['lat']))
                                                        else "")

        self.mainForm.SettCoordSpinBoxLon.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                        (self.mainForm.SettCoordSpinBoxLon.value() != float(
                                                            self.currentConfig['Coordinates']['lon']))
                                                        else "")

        self.mainForm.SettCoordSpinBoxHeight.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                           (self.mainForm.SettCoordSpinBoxHeight.value() !=
                                                            float(self.currentConfig['Coordinates']['height']))
                                                           else "")

        self.mainForm.SettCoordSpinBoxHorizont.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                           (self.mainForm.SettCoordSpinBoxHorizont.value() !=
                                                            int(self.currentConfig['Basic']['horizon']))
                                                           else "")

        self.mainForm.SettPathEditTLE.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                    (self.mainForm.SettPathEditTLE.text() != str(
                                                        self.currentConfig['Path']['tle_directory']))
                                                    else "")

        self.mainForm.SettPathEditCAT.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                    (self.mainForm.SettPathEditCAT.text() != str(
                                                        self.currentConfig['Path']['cat_directory']))
                                                    else "")

        self.mainForm.SettPathEditANG.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                    (self.mainForm.SettPathEditANG.text() != str(
                                                        self.currentConfig['Path']['ang_directory']))
                                                    else "")

        self.mainForm.SettPathCheckANG.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                     (self.mainForm.SettPathCheckANG.isChecked() != bool(
                                                         str2bool(self.currentConfig['Path']['delete_existing'])))
                                                     else "")

        self.mainForm.SettTLELoadBox.setStyleSheet("color: rgb(255, 0, 0);" if
                                                   (self.mainForm.SettTLELoadBox.isChecked() != bool(
                                                       str2bool(self.currentConfig['TLE']['download'])))
                                                   else "")

        self.mainForm.SettTLELoadLog.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                   (self.mainForm.SettTLELoadLog.text() != str(
                                                       self.currentConfig['TLE']['identity']))
                                                   else "")

        self.mainForm.SettTLELoadPass.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                    (self.mainForm.SettTLELoadPass.text() != str(
                                                        self.currentConfig['TLE']['password']))
                                                    else "")

    def clickedSave(self):

        confi = self.currentConfig

        self.currentConfig["System"]['threads'] = str(self.mainForm.SettSystemStreamEdit.value())

        self.currentConfig['Coordinates']['lat'] = str(self.mainForm.SettCoordSpinBoxLat.value())
        self.currentConfig['Coordinates']['lon'] = str(self.mainForm.SettCoordSpinBoxLon.value())
        self.currentConfig['Coordinates']['height'] = str(self.mainForm.SettCoordSpinBoxHeight.value())
        self.currentConfig['Basic']['horizon'] = str(self.mainForm.SettCoordSpinBoxHorizont.value())

        self.currentConfig['Path']['tle_directory'] = str(self.mainForm.SettPathEditTLE.text())
        self.currentConfig['Path']['cat_directory'] = str(self.mainForm.SettPathEditCAT.text())
        self.currentConfig['Path']['ang_directory'] = str(self.mainForm.SettPathEditANG.text())
        self.currentConfig['Path']['delete_existing'] = \
            "True" if (self.mainForm.SettPathCheckANG.isChecked()) else "False"

        self.currentConfig['TLE']['download'] = \
            "True" if (self.mainForm.SettTLELoadBox.isChecked()) else "False"
        self.currentConfig['TLE']['identity'] = str(self.mainForm.SettTLELoadLog.text())
        self.currentConfig['TLE']['password'] = str(self.mainForm.SettTLELoadPass.text())

        self.mainForm.manager.set_config(self.currentConfig)
        self.mainForm.manager.save_config_to_file("currentConfigView.conf")

        self.currentConfig = self.mainForm.manager.get_config()

        if not (self.currentConfig):
            print("Упс конфига нифига")
            return

        self.checkApplyConfig()
        self.configViewUpdate(self.currentConfig)

    def clickedCancel(self):
        self.configViewUpdate(self.currentConfig)
        self.checkApplyConfig()

    def setPathTLE(self):
        path = self.__getPathDir__()
        if path != "Err":
            self.mainForm.SettPathEditTLE.setText(path)

    def setPathCAT(self):
        path = self.__getPathDir__()
        if path != "Err":
            self.mainForm.SettPathEditCAT.setText(path)

    def setPathConf(self):
        path = self.__getPathDir__()
        if path != "Err":
            self.mainForm.SettPathEditFilterConf.setText(path)

    def setPathANG(self):
        path = self.__getPathDir__()
        if path != "Err":
            self.mainForm.SettPathEditANG.setText(path)

class ActionCalic():
    def __init__(self, mainForm: GuiFormMain):
        print("__init__ actionCalic")
        self.mainForm = mainForm

        self.currentConfig = self.mainForm.manager.get_config()  # To Do Перенести в Main

        if not (self.currentConfig):
            print("Упс конфига нифига")
            return

        self.calicViewUpdate(self.currentConfig)

        self.updateTleList(self.currentConfig['Path']['tle_directory'])

    # def updateTemplateList(self):
    #     print("updateTemplateList")

    def updateTleList(self, pathTleDir:str):
        # s  =  list(os.listdir(pathTleDir))
        for file in os.listdir(pathTleDir):
            if (file.find(".tle")):
                print(file)
        print("updateTleList")

    def calicViewUpdate(self, currentConfig):

        self.mainForm.calicPreFilterBox.setChecked(str2bool(currentConfig['Filter']['filter_enabled']))

        checkFiltName = str2bool(currentConfig['Filter']['filter_by_name'])
        self.mainForm.calicFilterNameBox.setChecked(bool(checkFiltName))
        self.mainForm.calicFilterNameEdit.setText(currentConfig['Filter']['names_string'])

        checkFiltPeriod = str2bool(currentConfig['Filter']['filter_by_period'])
        self.mainForm.calicFilterPeriodBox.setChecked(bool(checkFiltPeriod))
        self.mainForm.calicFilterPeriodEditMin.setValue(int(currentConfig['Filter']['min_period']))
        self.mainForm.calicFilterPeriodEditMax.setValue(int(currentConfig['Filter']['max_period']))

        self.mainForm.calicFilterTimeEditMin.setDateTime(
            datetime.datetime.strptime(currentConfig['Basic']['t_end'],"%Y-%m-%d %H:%M:%S"))
        self.mainForm.calicFilterTimeEditMax.setDateTime(
            datetime.datetime.strptime(currentConfig['Basic']['t_begin'],"%Y-%m-%d %H:%M:%S"))

        self.mainForm.calicFilterElevationBox.setChecked(
            bool(str2bool(currentConfig['Filter']['filter_by_elevation'])))
        self.mainForm.calicFilterElevationEditMin.setValue(int(currentConfig['Filter']['min_elevation']))
        self.mainForm.calicFilterElevationEditMax.setValue(int(currentConfig['Filter']['max_elevation']))

        self.mainForm.calicFilterSunliteBox.setChecked(
            bool(str2bool(currentConfig['Filter']['filter_by_sunlite'])))
        self.mainForm.calicFilterSunliteEdit.setValue(float(currentConfig['Filter']['sunlite']))

        self.mainForm.calicFilterDistanceBox.setChecked(
            bool(str2bool(currentConfig['Filter']['filter_by_distance'])))
        self.mainForm.calicFilterDistanceEditMin.setValue(int(currentConfig['Filter']['min_distance']))
        self.mainForm.calicFilterDistanceEditMax.setValue(int(currentConfig['Filter']['max_distance']))


class ActionView():
    def __init__(self, mainForm: GuiFormMain):

        print("__init__ actionView")
        self.mainForm = mainForm

        self.figGraphPolar, self.axGraphPolar = self.createGraphPolar()
        self.figGraphTime, self.axGraphTime = self.createGraphTime()

        self.mainForm.tableListKA.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.mainForm.tableListKA.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.mainForm.tableKAInfo.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.mainForm.tableKAInfo.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self.all_angs = self.mainForm.manager.get_ang_dict_with_data()
        self.ang_Line = dict()  # Time, TimeShadow, polar, polarShadow
        self.ang_Line_Check = set()  # Time, TimeShadow, polar, polarShadow

        # Select
        self.selectAngGraph = set()
        self.listCheckAng = set()

        self.selectEffectsSel = [pe.Stroke(linewidth=5, foreground='magenta'), pe.Normal()]
        self.selectEffectsUnsel = [pe.Stroke(), pe.Normal()]

        InfLable = list(zip(["NUMBER", "NAME", "ID", "COUNTRY", "LAUNCH", "PERIOD"],
                            ["OBJECT_NUMBER", "OBJECT_NAME", "OBJECT_ID", "COUNTRY", "LAUNCH", "PERIOD"]))

        self.importantInf = dict(zip(range(7), InfLable))

        self.updateKADate()


    def createGraphPolar(self):

        # print(hasattr(self, 'figGraphTime'))
        if (hasattr(self.mainForm, 'figGraphTime')):
            self.mainForm.figGraphPolar.add_subplot(projection='polar')
        else:
            fig, ax = plt.subplots(facecolor="#e5e5e5", subplot_kw={'projection': 'polar'})
            ax.set_facecolor("#e5e5e5")

        ax.set_theta_zero_location("N")  # Начало север
        ax.set_theta_direction(-1)  # Отразить

        ax.set_rlim(bottom=0, top=90, emit=1)  # Установите пределы обзора по радиальной оси

        ax.set_yticks(np.arange(0, 91, 15))  # Сетка

        ax.set_yticklabels([])

        # ax.set_yticklabels(ax.get_yticks()[::-1])
        # ax.set_rlabel_position(120)

        if (True):
            labels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            compass = [n / float(len(labels)) * 2 * np.pi for n in range(len(labels))]
            compass += compass[:1]
            plt.xticks(compass[:-1], labels)

        self.mainForm.layoutGraphPolar.addWidget(FigureCanvas(fig))
        self.mainForm.layoutGraphPolar.itemAt(0).widget().setMinimumSize(QtCore.QSize(300, 300))
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
        ax.grid(axis='x', which='minor', linewidth=1.5)

        ax.format_coord = lambda x, y: 'Elevation = ' + format(y, '1.2f') + ', ' + \
                                       'Date = ' + num2date(x).strftime("%H:%M:%S\n%d/%m/%Y")

        # TO DO includ limits for zoom

        self.mainForm.layoutBottGrph.addWidget(FigureCanvas(fig))
        self.mainForm.layoutBottGrph.itemAt(0).widget().setMinimumSize(QtCore.QSize(0, 300))
        toolbar = NavigationToolbar(fig.canvas, self.mainForm)
        self.mainForm.layoutBottGrph.addWidget(toolbar)

        return fig, ax


    def updateKADate(self):

        if (bool(self.all_angs)):

            for norad_id in self.all_angs.keys():

                itemKa = QTreeWidgetItem(self.mainForm.tableListKA)
                itemKa.setFlags(itemKa.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                itemKa.setCheckState(0, Qt.Unchecked)
                itemKa.setData(0, Qt.EditRole, norad_id)

                current_sat = self.all_angs.get(norad_id)  # Получить анги

                for ang in current_sat.keys():

                    if (len(current_sat) > 1):

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
                        itemKa.setTextAlignment(1, Qt.AlignHCenter | Qt.AlignVCenter)

                    d = current_sat.get(ang)
                    # --------Отрисовка на графиках---------

                    df_shadow = d[d["Ph"] == 0.0]
                    df_shine = d[d["Ph"] != 0.0]

                    self.ang_Line[ang] = [
                        self.axGraphTime.plot(df_shine.Time.values, df_shine.Elev.values, linewidth=2, )[0],
                        self.axGraphTime.plot(df_shadow.Time.values, df_shadow.Elev.values,
                                              linewidth=1, color="grey")[0],
                        # linewidth= 1, color="grey", marker='.' , markersize = 1)[0],

                        self.axGraphPolar.plot(np.deg2rad(df_shine.Az.values), 90 - (df_shine.Elev.values),
                                               visible=False, linewidth=2)[0],
                        self.axGraphPolar.plot(np.deg2rad(df_shadow.Az.values), 90 - (df_shadow.Elev.values),
                                               visible=False, linewidth=1, color="grey")[0]
                        # visible = False, linewidth = 1, color = "grey", marker = '.', markersize = 1)[0]
                    ]
                    # ========================================
                # self.tableListKA.addTopLevelItem(itemKa);
        else:
            print("amgs_isEmpty")

    def fillKaInfo(self, idKa: int):
        # print("fillKaInfo")

        dataKA = self.mainForm.manager.get_sat_info(idKa)

        for idInf, titleInf in self.importantInf.items():
            self.mainForm.tableKAInfo.insertRow(idInf)

            itemLable = QTableWidgetItem()
            itemLable.setData(Qt.EditRole, titleInf[0])
            self.mainForm.tableKAInfo.setItem(idInf, 0, itemLable)

            itemInf = QTableWidgetItem()
            itemInf.setData(Qt.EditRole, str(dataKA[titleInf[1]].values[0]))
            self.mainForm.tableKAInfo.setItem(idInf, 1, itemInf)

    def slotSelectKaList(self):
        start_time = time.time()

        newSelectAng = set()

        if not (self.selectAngGraph):  # нет выбранных
            print()
            for keyLines in self.ang_Line_Check if bool(self.ang_Line_Check) else self.ang_Line.keys():
                self.ang_Line[keyLines][0].set(lw=2, alpha=0.2, path_effects=[pe.Stroke(), pe.Normal()])
                self.ang_Line[keyLines][1].set(lw=1, alpha=0.2, path_effects=[pe.Stroke(), pe.Normal()])

        self.mainForm.tableKAInfo.clear()

        selectedColumns = self.mainForm.tableListKA.selectedItems()

        # Заполнение информации
        if (len(selectedColumns) == 1):
            idKA = (int(selectedColumns[0].data(0, Qt.EditRole)
                        if (selectedColumns[0].parent() is None)
                        else selectedColumns[0].parent().data(0, Qt.EditRole)))

            self.fillKaInfo(idKA)

        # ===========================
        # Selected New
        for item in selectedColumns:

            if item.data(1, Qt.EditRole) in self.selectAngGraph:
                newSelectAng.add(item.data(1, Qt.EditRole))
                continue  # Если КА уже отображён

            if (item.childCount() == 0):
                newSelectAng.add(
                    self.selectGraph(item.data(1, Qt.EditRole))
                )

            else:
                for childIndex in range(item.childCount()):  # проход по вложенным
                    newSelectAng.add(
                        self.selectGraph(item.child(childIndex).data(1, Qt.EditRole))
                    )

        # ===========================
        #   Unselected old
        for item in self.selectAngGraph - newSelectAng:
            self.selectAngGraph.discard(
                self.selectGraph(item, True)
            )

        self.selectAngGraph.update(newSelectAng)

        # print('repaint time: ', time.time() - start_time)

        self.figGraphPolar.canvas.draw()
        self.figGraphPolar.canvas.flush_events()
        self.figGraphTime.canvas.draw()
        self.figGraphTime.canvas.flush_events()
        self.mainForm.repaint()

        # print('end time: ', time.time() - start_time)
        # print("\n")

    def selectGraph(self, angName: str, unselection=False) -> str:

        self.ang_Line[angName][0].set(lw=3, zorder=2 if (unselection) else 3,
                                      alpha=0.1 if (unselection) else 1,
                                      path_effects=self.selectEffectsUnsel if
                                      (unselection) else
                                      self.selectEffectsSel)
        self.ang_Line[angName][1].set(lw=2, zorder=2 if (unselection) else 3,
                                      alpha=0.1 if (unselection) else 1,
                                      path_effects=self.selectEffectsUnsel if
                                      (unselection) else
                                      self.selectEffectsSel)
        self.ang_Line[angName][2].set_visible(not unselection)
        self.ang_Line[angName][3].set_visible(not unselection)

        return angName

    def selectionReset(self):

        for item in self.selectAngGraph:
            self.selectGraph(item, True)
        self.selectAngGraph.clear()

        size2 = len(self.selectAngGraph) == 0
        if (size2):  # нет выбранных
            for keyLines in self.ang_Line_Check if bool(self.ang_Line_Check) else self.ang_Line.keys():
                self.ang_Line[keyLines][0].set(lw=2, alpha=1, path_effects=[pe.Stroke(), pe.Normal()])
                self.ang_Line[keyLines][1].set(lw=1, alpha=1, path_effects=[pe.Stroke(), pe.Normal()])

        self.figGraphPolar.canvas.draw()
        self.figGraphTime.canvas.draw()

    def showOnlyMarked(self, checkState=True):

        for angSet in self.ang_Line.values():
            angSet[0].set_visible(not checkState)
            angSet[1].set_visible(not checkState)

        for itemKA in self.mainForm.tableListKA.findItems("*", Qt.MatchRegExp | Qt.MatchWildcard, 0):

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

