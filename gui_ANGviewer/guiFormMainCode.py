import pandas as pd

import manager
from manager import EffectiveManager
from gui_ANGviewer.guiFormMainAngView import *

from builtins import type, print
import os
from copy import deepcopy

import threading
from time import sleep

from datetime import datetime, date

import collections

from configparser import ConfigParser, NoSectionError, NoOptionError

import numpy as np
from numpy.distutils.fcompiler import str2bool
from pandas import date_range, NaT

from PyQt5.Qt import *
from PyQt5.QtWidgets import *

from matplotlib import (use,
                        pyplot as plt,
                        patheffects as pe)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.dates import AutoDateLocator, ConciseDateFormatter, num2date

use('Qt5Agg')


# plt.style.use('https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle')
# date_form = DateFormatter("%H:%M:%S")

class GuiFormMain(QtWidgets.QMainWindow, Ui_guiFormMain):
    """
    Окно графического интерфейса
    """

    def __init__(self, current_manager: EffectiveManager = None, show_masseuse_method=None):
        """

        :param current_manager: Математический модуль
        :param show_masseuse_method: Метод вывода состояния при загрузке
        """
        if current_manager is None or show_masseuse_method is None:
            raise ValueError("Ошибка создания GuiFormMain")

        QMainWindow.__init__(self)
        self.setupUi(self)

        self.name_current_config = "currentConfigView.conf"

        self.manager = current_manager
        self.current_config = self.manager.get_config()

        # если ошибка в чтении конфигурации
        if self.current_config is None:
            raise ValueError("Ошибка создания ошибка в чтении конфигурации")

        self.status_gui = "Инициализация интерфейса"
        self.show_massage_method = show_masseuse_method

        self.flag_checked_state = True
        self.loop_check = threading.Thread(target=loop_check_manager_state,
                                           args=(self, self.manager), name="loop_check")
        self.loop_check.start()

        # ------------------------------------------------------------------
        self.menu_action_group = QActionGroup(self)

        self.menu_action_group.addAction(self.buttSetting)
        self.menu_action_group.addAction(self.buttCalicANG)
        self.menu_action_group.addAction(self.buttViewer)

        self.buttSetting.changed.connect(lambda: self.tabWidget.setCurrentIndex(0))
        self.buttCalicANG.changed.connect(lambda: self.tabWidget.setCurrentIndex(1))
        self.buttViewer.changed.connect(lambda: self.tabWidget.setCurrentIndex(2))

        # ----------------------------Setting--------------------------------
        self.actionSettings = ActionSettings(self)

        self.SettCatUpdateButt.clicked.connect(self.actionSettings.clicked_cat_update)
        self.SettPathButtTLE.clicked.connect(self.actionSettings.setPathTLE)
        self.SettPathButtCAT.clicked.connect(self.actionSettings.setPathCAT)
        self.SettPathButtANG.clicked.connect(self.actionSettings.setPathANG)
        self.SettButtSeve.clicked.connect(self.actionSettings.clickedSave)
        self.SettButtCancel.clicked.connect(self.actionSettings.clickedCancel)
        # ----------------------------Calic---------------------------------

        self.action_calculate = ActionCalculate(self)

        self.calicTemplateList.currentTextChanged.connect(self.action_calculate.filter_list_select)

        self.calicTemplateButSeveAs.clicked.connect(self.action_calculate.calic_butt_filter_save_as)
        self.calicTemplateButSeve.clicked.connect(self.action_calculate.calic_butt_filter_save)
        self.calicTemplateButDel.clicked.connect(self.action_calculate.calic_butt_filter_del)
        self.calicTemplateButCancel.clicked.connect(self.action_calculate.calic_butt_filter_cansel)

        self.calicTLEUpdateListButt.clicked.connect(self.action_calculate.calic_butt_update_all_lists)
        self.calicTLEUpdateButt.clicked.connect(self.action_calculate.calic_butt_tle_update)

        self.calicFilterTimeButt.clicked.connect(self.action_calculate.calc_butt_data_time_now)

        self.calicFilterByTypeCheckPayload.toggled.connect(
            lambda check_new_state:
            self.action_calculate.least_one_mark(self.calicFilterByTypeCheckPayload))
        self.calicFilterByTypeCheckBody.toggled.connect(
            lambda check_new_state:
            self.action_calculate.least_one_mark(self.calicFilterByTypeCheckBody))
        self.calicFilterByTypeCheckDebris.toggled.connect(
            lambda check_new_state:
            self.action_calculate.least_one_mark(self.calicFilterByTypeCheckDebris))

        self.calicButtApply.clicked.connect(
            lambda: self.action_calculate.filter_list_apply_or_save(current_config=self.current_config,
                                                                    flag_save_as_mold=False)
        )
        self.calicButtCancel.clicked.connect(self.action_calculate.calic_butt_filter_cansel)

        self.calicStartButt.clicked.connect(self.action_calculate.calic_butt_start)
        self.calicStopButt.clicked.connect(self.action_calculate.calic_butt_stop)
        self.calicClearAngDirButt.clicked.connect(self.action_calculate.calic_butt_clear_ang_dir)

        # ----------------------------View---------------------------------
        self.action_view = ActionView(self)
        self.thread_update_KA = threading.Thread(target=self.action_view.update_ka_data,
                                                 args=())

        self.tableListKA.itemSelectionChanged.connect(self.action_view.slotSelectKaList)
        self.buttResetSelection.released.connect(self.action_view.view_butt_selection_reset)
        self.buttOnlyCheck.clicked.connect(self.action_view.view_butt_show_only_marked)

        self.viewButtCliarCU.released.connect(self.action_view.clear_KA)
        self.viewButtUpdateCU.clicked.connect(self.action_view.update_ka_data)
        self.viewButtMoveCU.clicked.connect(self.action_view.view_butt_move_cu)

        self.viewButtSieve.clicked.connect(self.action_view.view_butt_sieve)

        # после загрузки переключаем метод вывода сообщений
        self.show_massage_method = self.statusbar.showMessage

    def closeEvent(self, event):
        self.flag_checked_state = False
        self.loop_check.join()

    def get_status(self) -> str:
        """
        Выдача статуса граф интерфейса
        :return: Статус
        """
        return self.status_gui

    def set_tab_view_current_index(self, currentIndex: int = 0):
        """
        Переключение панелей на индекс
        :param currentIndex:
        :return:
        """

        if currentIndex < 0 or currentIndex > 2:
            return

        self.tabWidget.setCurrentIndex(currentIndex)
        self.menu_action_group.actions()[currentIndex].setChecked(True)


def loop_check_manager_state(gui_form: GuiFormMain = None,
                             current_manager: EffectiveManager = None,
                             ):
    """
    Функция опроса и вывода состояния

    Статус выбродится только если он изменился
    :param gui_form: Графический интерфейс
    :param current_manager: ядро расчётов
    :return:
    """

    if gui_form is None or current_manager is None:
        return None

    old_status = ""

    while gui_form.flag_checked_state:

        new_status = f"{current_manager.get_status()}  {gui_form.get_status()}"

        if old_status != new_status:
            gui_form.show_massage_method(new_status)
            old_status = new_status
        # gui_form.repaint()
        sleep(0.2)

    print("loopCheckManagerStateFinish")


class ActionSettings:
    """
    Клас взаимодействия с окном настроек
    """

    def __init__(self, main_form: GuiFormMain = None):
        """
        Конструктор класса обработки взаимодействий с окном настроек
        :param main_form: Экземпляр главной формы
        """
        # print("__init__ actionSettings")
        if main_form is None:
            raise ValueError("Ошибка создания ActionSettings")

        self.main_form = main_form

        # self.main_form.SettSystemStreamLabel.setVisible(False)
        # self.main_form.SettSystemStreamEdit.setVisible(False)
        self.main_form.SettPathCheckANG.setVisible(False)

        self.check_enable_calic()

        self.configViewUpdate(self.main_form.current_config)

        if not os.path.exists(os.path.join(os.getcwd(),
                                           self.main_form.name_current_config)):
            self.clickedSave()

    def check_enable_calic(self):
        """
        Установить доступность элементов
        управления в соответствии с конфигом
        :return:
        """
        # Проверка заполнения координат
        coord_and_dir_ok = True
        if ((not self.main_form.current_config['Coordinates']['lat']) or
                (not self.main_form.current_config['Coordinates']['lon']) or
                (not self.main_form.current_config['Coordinates']['height']) or
                (not self.main_form.current_config['Basic']['horizon']) or
                # (not self.main_form.current_config['Path']['tle_directory']) or
                # (not self.main_form.current_config['Path']['cat_directory']) or
                (not self.main_form.current_config['Path']['ang_directory'])):
            # self.main_form.tabWidget.setCurrentIndex(0)
            self.main_form.set_tab_view_current_index(0)
            coord_and_dir_ok = False
        self.main_form.tabCalic.setEnabled(coord_and_dir_ok)
        self.main_form.tabViewer.setEnabled(coord_and_dir_ok)

        # Проверка заполнения TLE Директории
        tle_ok = True
        if ((not self.main_form.current_config['TLE']['identity']) or
                (not self.main_form.current_config['TLE']['identity'])):
            tle_ok = False
        self.main_form.calicTLEUpdateButt.setEnabled(tle_ok)

    def configViewUpdate(self, current_config: dict[str, dict] = None):
        """
        Обновить поля в соответствии с currentConfig
        :param current_config:
        :return:
        """
        if current_config is None:
            current_config = dict()

        if not current_config:
            return

        self.main_form.SettCatUpdateLabel.setText(
            f"Дата формирования каталога КА  {self.main_form.manager.get_catalog_date().strftime('%d-%m-%Y %H:%M')}")

        self.main_form.SettSystemStreamEdit.setValue(int(current_config["System"]['threads']))

        self.main_form.SettCoordSpinBoxLat.setValue(float(current_config['Coordinates']['lat']))
        self.main_form.SettCoordSpinBoxLon.setValue(float(current_config['Coordinates']['lon']))
        self.main_form.SettCoordSpinBoxHeight.setValue(float(current_config['Coordinates']['height']))
        self.main_form.SettCoordSpinBoxHorizont.setValue(int(current_config['Basic']['horizon']))

        self.main_form.SettPathEditTLE.setText(current_config['Path']['tle_directory'])
        self.main_form.SettPathEditCAT.setText(current_config['Path']['cat_directory'])
        self.main_form.SettPathEditANG.setText(current_config['Path']['ang_directory'])

        self.main_form.SettTLELoadLog.setText(current_config['TLE']['identity'])
        self.main_form.SettTLELoadPass.setText(current_config['TLE']['password'])

        self.check_enable_calic()

    def __get_path_dir__(self) -> str:
        """
        Вызов Диалогового окна для указания имени директорий\n
        директория папка находится в директории программы
        :return:
        """

        cwd = os.getcwd()
        path = os.path.normpath(QFileDialog.getExistingDirectory(self.main_form,
                                                                 "Open Directory",
                                                                 cwd,
                                                                 QFileDialog.ShowDirsOnly |
                                                                 QFileDialog.DontResolveSymlinks |
                                                                 QFileDialog.DontUseNativeDialog
                                                                 ))
        if path.find(cwd) < 0:
            return "Err"

        return path.replace(cwd, '')[1:]

    def checkApplyConfig(self):
        """
        Проверка изменения конфига

        :return:
        """

        self.main_form.SettSystemStreamEdit.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                          (self.main_form.SettSystemStreamEdit.value() != int(
                                                              self.main_form.current_config["System"]['threads']))
                                                          else "")

        self.main_form.SettCoordSpinBoxLat.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                         (self.main_form.SettCoordSpinBoxLat.value() != float(
                                                             self.main_form.current_config['Coordinates']['lat']))
                                                         else "")

        self.main_form.SettCoordSpinBoxLon.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                         (self.main_form.SettCoordSpinBoxLon.value() != float(
                                                             self.main_form.current_config['Coordinates']['lon']))
                                                         else "")

        self.main_form.SettCoordSpinBoxHeight.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                            (self.main_form.SettCoordSpinBoxHeight.value() !=
                                                             float(
                                                                 self.main_form.current_config['Coordinates'][
                                                                     'height']))
                                                            else "")

        self.main_form.SettCoordSpinBoxHorizont.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                              (self.main_form.SettCoordSpinBoxHorizont.value() !=
                                                               int(self.main_form.current_config['Basic']['horizon']))
                                                              else "")

        self.main_form.SettPathEditTLE.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                     (self.main_form.SettPathEditTLE.text() != str(
                                                         self.main_form.current_config['Path']['tle_directory']))
                                                     else "")

        self.main_form.SettPathEditCAT.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                     (self.main_form.SettPathEditCAT.text() != str(
                                                         self.main_form.current_config['Path']['cat_directory']))
                                                     else "")

        self.main_form.SettPathEditANG.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                     (self.main_form.SettPathEditANG.text() != str(
                                                         self.main_form.current_config['Path']['ang_directory']))
                                                     else "")

        # self.main_form.SettPathCheckANG.setStyleSheet("background-color: rgb(255, 0, 0);" if
        #                                               (self.main_form.SettPathCheckANG.isChecked() != bool(
        #                                                   str2bool(
        #                                                       self.main_form.current_config['Path'][
        #                                                           'delete_existing'])))
        #                                               else "")

        # self.mainForm.SettTLELoadBox.setStyleSheet("color: rgb(255, 0, 0);" if
        #                                            (self.mainForm.SettTLELoadBox.isChecked() != bool(
        #                                                str2bool(self.currentConfig['TLE']['download'])))
        #                                            else "")

        self.main_form.SettTLELoadLog.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                    (self.main_form.SettTLELoadLog.text() != str(
                                                        self.main_form.current_config['TLE']['identity']))
                                                    else "")

        self.main_form.SettTLELoadPass.setStyleSheet("background-color: rgb(255, 0, 0);" if
                                                     (self.main_form.SettTLELoadPass.text() != str(
                                                         self.main_form.current_config['TLE']['password']))
                                                     else "")

    def clicked_cat_update(self):
        """
        Обработка нажатия кнопки:\n
        Обновление каталога аппаратов
        :return:
        """

        self.main_form.SettCatUpdateButt.setEnabled(False)
        self.main_form.show_massage_method("Обновление каталога")
        self.main_form.repaint()

        self.main_form.manager.download_cat()
        self.configViewUpdate(self.main_form.current_config)

        self.main_form.SettCatUpdateButt.setEnabled(True)
        self.main_form.show_massage_method("")
        self.main_form.repaint()

    def clickedSave(self):
        """
        Обработка нажатия кнопки:\n
        Сохранение и применение настроек
        :return:
        """
        if not self.main_form.current_config:
            print("Отсутствует файл конфигурации")
            return

        self.main_form.SettButtSeve.setEnabled(False)

        # Коректирование конфига
        self.main_form.current_config["System"]['threads'] = str(self.main_form.SettSystemStreamEdit.value())

        self.main_form.current_config['Coordinates']['lat'] = str(self.main_form.SettCoordSpinBoxLat.value())
        self.main_form.current_config['Coordinates']['lon'] = str(self.main_form.SettCoordSpinBoxLon.value())
        self.main_form.current_config['Coordinates']['height'] = str(self.main_form.SettCoordSpinBoxHeight.value())
        self.main_form.current_config['Basic']['horizon'] = str(self.main_form.SettCoordSpinBoxHorizont.value())

        self.main_form.current_config['Path']['tle_directory'] = str(self.main_form.SettPathEditTLE.text())
        self.main_form.current_config['Path']['cat_directory'] = str(self.main_form.SettPathEditCAT.text())
        self.main_form.current_config['Path']['ang_directory'] = str(self.main_form.SettPathEditANG.text())
        # self.main_form.current_config['Path']['delete_existing'] = \
        #     "True" if (self.main_form.SettPathCheckANG.isChecked()) else "False"

        # self.currentConfig['TLE']['download'] = \
        #     "True" if (self.mainForm.SettTLELoadBox.isChecked()) else "False"
        self.main_form.current_config['TLE']['identity'] = str(self.main_form.SettTLELoadLog.text())
        self.main_form.current_config['TLE']['password'] = str(self.main_form.SettTLELoadPass.text())

        # применение конфига
        self.main_form.manager.set_config(self.main_form.current_config)
        # Сохраниие конфига
        self.main_form.manager.save_config_to_file(self.main_form.name_current_config)

        # Загрузка конфига
        self.main_form.current_config = self.main_form.manager.get_config()

        # Проверка конфига и отображение
        self.checkApplyConfig()
        self.configViewUpdate(self.main_form.current_config)

        self.main_form.SettButtSeve.setEnabled(True)

    def clickedCancel(self):
        """
        Обработка нажатия кнопки:\n
        Выбрать отмены изменений
        :return:
        """
        self.configViewUpdate(self.main_form.current_config)

    def setPathTLE(self):
        path = self.__get_path_dir__()
        if path != "Err":
            self.main_form.SettPathEditTLE.setText(path)

    def setPathCAT(self):
        path = self.__get_path_dir__()
        if path != "Err":
            self.main_form.SettPathEditCAT.setText(path)

    def setPathConf(self):
        path = self.__get_path_dir__()
        if path != "Err":
            self.main_form.SettPathEditFilterConf.setText(path)

    def setPathANG(self):
        """
        Обработка нажатия кнопки:\n
        Выбрать директорию ANG файлов
        :return:
        """

        path = self.__get_path_dir__()
        if path != "Err":
            self.main_form.SettPathEditANG.setText(path)


class ActionCalculate:
    """
    Клас взаимодействия с окном расчёта и фильтрации
    """

    def __init__(self, main_form: GuiFormMain = None):
        # print("__init__ actionCalic")
        """
        Конструктор класса обработки взаимодействий с окном расчёта
        :param main_form: Экземпляр главной формы
        """

        if main_form is None:
            raise ValueError("Ошибка создания ActionCalculate")

        self.path_filter_dir = "viewFilterTemplates"

        self.main_form = main_form
        # self.main_form.calicFilterLaunchBox.setVisible(False)
        # self.main_form.calicFilterInclinaBox.setVisible(False)
        self.main_form.calicStopButt.setEnabled(False)
        self.main_form.calicTemplateButDel.setEnabled(False)
        self.main_form.calicTemplateButSeve.setEnabled(False)

        self.main_form.calicSystemStreamEdit.setVisible(False)
        self.main_form.calicSystemStreamLabel.setVisible(False)

        # self.current_config = self.main_form.manager.get_config()  # To Do Перенести в Main

        if not self.main_form.current_config:
            print("Упс конфига нифига")
            return

        self.filter_list_update()
        self.calic_view_update(self.main_form.current_config)
        self.filter_tle_list_update(self.main_form.current_config['Path']['tle_directory'])

        self.main_form.calicTLECastomRadio.toggled.connect(self.main_form.calicTLEList.setEnabled)

        self.main_form.calicFilterPeriodEditMin.setMaximum(self.main_form.
                                                           calicFilterPeriodEditMax.value())
        self.main_form.calicFilterPeriodEditMax.setMinimum(self.main_form.
                                                           calicFilterPeriodEditMin.value())
        self.main_form.calicFilterPeriodEditMin.valueChanged.connect(
            lambda value: self.main_form.calicFilterPeriodEditMax.setMinimum(value))
        self.main_form.calicFilterPeriodEditMax.valueChanged.connect(
            lambda value: self.main_form.calicFilterPeriodEditMin.setMaximum(value))

        self.main_form.calicFilterElevationEditMin.setMaximum(self.main_form.
                                                              calicFilterElevationEditMax.value())
        self.main_form.calicFilterElevationEditMax.setMinimum(self.main_form.
                                                              calicFilterElevationEditMin.value())
        self.main_form.calicFilterElevationEditMin.valueChanged.connect(
            lambda value: self.main_form.calicFilterElevationEditMax.setMinimum(value))
        self.main_form.calicFilterElevationEditMax.valueChanged.connect(
            lambda value: self.main_form.calicFilterElevationEditMin.setMaximum(value))

        self.main_form.calicFilterDistanceEditMin.setMaximum(self.main_form.
                                                             calicFilterDistanceEditMax.value())
        self.main_form.calicFilterDistanceEditMax.setMinimum(self.main_form.
                                                             calicFilterDistanceEditMin.value())
        self.main_form.calicFilterDistanceEditMin.valueChanged.connect(
            lambda value: self.main_form.calicFilterDistanceEditMax.setMinimum(value))
        self.main_form.calicFilterDistanceEditMax.valueChanged.connect(
            lambda value: self.main_form.calicFilterDistanceEditMin.setMaximum(value))

    def calic_view_update(self, current_config: dict[str, dict] = None):
        """
        Заполнение полей согласно фильтру
        :param current_config:
        :return:
        """

        if current_config is None:
            return

        try:
            self.main_form.calicPreFilterBox.setChecked(str2bool(current_config['Filter']['filter_enabled']))

            check_filter_name = str2bool(current_config['Filter']['filter_by_name'])
            self.main_form.calicFilterNameBox.setChecked(bool(check_filter_name))
            self.main_form.calicFilterNameEdit.setText(str(current_config['Filter']['names_string']).
                                                       replace("|", ", "))

            check_filter_period = str2bool(current_config['Filter']['filter_by_period'])
            self.main_form.calicFilterPeriodBox.setChecked(bool(check_filter_period))
            self.main_form.calicFilterPeriodEditMin.setValue(float(current_config['Filter']['min_period']))
            self.main_form.calicFilterPeriodEditMax.setValue(float(current_config['Filter']['max_period']))

            if current_config['TLE']['user_file']:
                if self.main_form.calicTLEList.findItems(current_config['TLE']['user_file'],
                                                         Qt.MatchRegExp | Qt.MatchWildcard):

                    self.main_form.calicTLECastomRadio.setChecked(True)
                    self.main_form.calicTLEList.findItems(current_config['TLE']['user_file'],
                                                          Qt.MatchRegExp | Qt.MatchWildcard)[0].setSelected(True)
                else:
                    self.main_form.calicTLEList.setCurrentRow(-1)
            else:
                self.main_form.calicTLEAllRadio.setChecked(True)

            self.main_form.calicFilterTimeEditMin.setDateTime(
                datetime.strptime(current_config['Basic']['t_begin'], "%Y-%m-%d %H:%M:%S"))
            self.main_form.calicFilterTimeEditMax.setDateTime(
                datetime.strptime(current_config['Basic']['t_end'], "%Y-%m-%d %H:%M:%S"))

            self.main_form.calicFilterElevationBox.setChecked(
                bool(str2bool(current_config['Filter']['filter_by_elevation'])))
            self.main_form.calicFilterElevationEditMin.setValue(int(current_config['Filter']['min_elevation']))
            self.main_form.calicFilterElevationEditMax.setValue(int(current_config['Filter']['max_elevation']))

            self.main_form.calicFilterSunliteBox.setChecked(
                bool(str2bool(current_config['Filter']['filter_by_sunlite'])))
            self.main_form.calicFilterSunliteEdit.setValue(float(current_config['Filter']['sunlite']))

            self.main_form.calicFilterDistanceBox.setChecked(
                bool(str2bool(current_config['Filter']['filter_by_distance'])))
            self.main_form.calicFilterDistanceEditMin.setValue(int(current_config['Filter']['min_distance']))
            self.main_form.calicFilterDistanceEditMax.setValue(int(current_config['Filter']['max_distance']))

            self.main_form.calicFilterByTypeBox.setChecked(
                bool(str2bool(current_config['Filter']['filter_by_type'])))
            self.main_form.calicFilterByTypeCheckBody.setChecked(
                bool(str2bool(current_config['Filter']['type_body'])))
            self.main_form.calicFilterByTypeCheckPayload.setChecked(
                bool(str2bool(current_config['Filter']['type_payload'])))
            self.main_form.calicFilterByTypeCheckDebris.setChecked(
                bool(str2bool(current_config['Filter']['type_debris'])))

            # self.main_form.calcSystemStreamEdit.setValue(int(current_config['System']['threads']))
            self.main_form.calicCheckClearCuDir.setChecked(str2bool(current_config['Path']['delete_existing']))
            self.main_form.calicCheckCalculatePhase.setChecked(str2bool(current_config['Basic']['calculate_phase']))
        except KeyError as e:
            print(f"Ошибка чтения конфигурации Ключ {e}")

    def least_one_mark(self, currentCheckBoxType: QtWidgets.QCheckBox):
        """
        Механизм заперта снятия последней галочки в типах объектов
        :param currentCheckBoxType: CheckBox котрый вызвал событие
        :return:
        """

        if not ((self.main_form.calicFilterByTypeCheckPayload.isChecked()) or
                (self.main_form.calicFilterByTypeCheckBody.isChecked()) or
                (self.main_form.calicFilterByTypeCheckDebris.isChecked())):
            currentCheckBoxType.setChecked(Qt.Checked)

    def filter_list_update(self):
        """
        Обновление списка сохранённых фильтров
        :return:
        """

        if not self.path_filter_dir:
            return

        self.main_form.calicTemplateList.clear()

        # Если директории с фильтрами нет Создаём и выходим
        if not os.path.exists(self.path_filter_dir):
            os.mkdir(os.path.join(os.getcwd(), self.path_filter_dir))
            return

        for file in os.listdir(self.path_filter_dir):
            if file.find(".conf") != -1:
                item_file = QListWidgetItem()
                item_file.setText(file)
                self.main_form.calicTemplateList.addItem(item_file)

        self.main_form.calicTemplateList.setCurrentRow(-1)
        # self.main_form.tabCalic.setFocus(self.main_form.calicButtCancel)

    def filter_list_apply_or_save(self, mold_name: str = '', current_config: dict[str, dict] = None,
                                  flag_save_as_mold: bool = True):
        """
        Применение параметров фильтрации или сохранение в шаблон
        :param mold_name: имя шаблона фильтра если flag_save_as_mold = True
        :param current_config: текущая конфигурация
        :param flag_save_as_mold: флаг сохранения как шаблон
        :return:
        """

        if (not mold_name) and flag_save_as_mold:
            return

        if current_config is None:
            current_config = dict()

        filter_mold = dict() if flag_save_as_mold else current_config

        if not ("TLE" in filter_mold.keys()):
            filter_mold.update({"TLE": dict()})
        if self.main_form.calicTLEAllRadio.isChecked():
            filter_mold["TLE"].update({"user_file": ""})
        else:
            filter_mold["TLE"].update(
                {"user_file": self.main_form.calicTLEList.selectedItems()[0].text()})

        if not ("Basic" in filter_mold.keys()):
            filter_mold.update({"Basic": dict()})
        filter_mold["Basic"].update(
            {'t_begin': self.main_form.calicFilterTimeEditMin.dateTime().toString(
                "yyyy-MM-dd hh:mm:ss")})
        filter_mold["Basic"].update(
            {'t_end': self.main_form.calicFilterTimeEditMax.dateTime().toString(
                "yyyy-MM-dd hh:mm:ss")})

        filter_mold["Basic"].update(
            {'calculate_phase': "True" if (self.main_form.calicCheckCalculatePhase.isChecked()) else "False"})

        if not ("Filter" in filter_mold.keys()):
            filter_mold.update({"Filter": dict()})

        filter_mold["Filter"].update(
            {'filter_enabled': "True" if (self.main_form.calicPreFilterBox.isChecked()) else "False"})

        filter_mold["Filter"].update(
            {'filter_by_name': "True" if (self.main_form.calicFilterNameBox.isChecked()) else "False"})

        filter_mold["Filter"].update({'names_string':
            "|".join(
                word.strip() for word in self.main_form.calicFilterNameEdit.text().split(",") if word != " ")})

        filter_mold["Filter"].update(
            {'filter_by_period': "True" if (self.main_form.calicFilterPeriodBox.isChecked()) else "False"})
        filter_mold["Filter"].update({'min_period': str(self.main_form.calicFilterPeriodEditMin.value())})
        filter_mold["Filter"].update({'max_period': str(self.main_form.calicFilterPeriodEditMax.value())})

        filter_mold["Filter"].update(
            {'filter_by_elevation': "True" if (self.main_form.calicFilterElevationBox.isChecked()) else "False"})
        filter_mold["Filter"].update({'min_elevation': str(self.main_form.calicFilterElevationEditMin.value())})
        filter_mold["Filter"].update({'max_elevation': str(self.main_form.calicFilterElevationEditMax.value())})

        filter_mold["Filter"].update(
            {'filter_by_sunlite': "True" if (self.main_form.calicFilterSunliteBox.isChecked()) else "False"})
        filter_mold["Filter"].update({'sunlite': str(self.main_form.calicFilterSunliteEdit.value())})

        filter_mold["Filter"].update(
            {'filter_by_distance': "True" if (self.main_form.calicFilterDistanceBox.isChecked()) else "False"})
        filter_mold["Filter"].update({'min_distance': str(self.main_form.calicFilterDistanceEditMin.value())})
        filter_mold["Filter"].update({'max_distance': str(self.main_form.calicFilterDistanceEditMax.value())})

        filter_mold["Filter"].update(
            {'filter_by_type': "True" if (self.main_form.calicFilterByTypeBox.isChecked()) else "False"})
        filter_mold["Filter"].update(
            {'type_body': "True" if (self.main_form.calicFilterByTypeCheckBody.isChecked()) else "False"})
        filter_mold["Filter"].update(
            {'type_payload': "True" if (self.main_form.calicFilterByTypeCheckPayload.isChecked()) else "False"})
        filter_mold["Filter"].update(
            {'type_debris': "True" if (self.main_form.calicFilterByTypeCheckDebris.isChecked()) else "False"})

        # if not ("System" in filter_mold.keys()):
        #     filter_mold.update({"System": dict()})
        # filter_mold["System"].update({"threads": str(self.main_form.calicSystemStreamEdit.value())})

        if not ("Path" in filter_mold.keys()):
            filter_mold.update({"Path": dict()})
        filter_mold["Path"].update(
            {"delete_existing": "True" if (self.main_form.calicCheckClearCuDir.isChecked()) else "False"})

        if flag_save_as_mold:
            save_mold_to_file(filter_mold, self.path_filter_dir, mold_name)
        else:
            self.main_form.manager.set_config(self.main_form.current_config)
            self.main_form.manager.save_config_to_file(self.main_form.name_current_config)
            self.main_form.current_config = self.main_form.manager.get_config()
            self.calic_view_update(self.main_form.current_config)

        # print("seveFilterMold")

    def filter_list_select(self, text_select_row: str = None):
        """
        Заполние таблицы с фильтрами конфигурации фильтров

        :param text_select_row: Текст выбранной ячейки
        """

        if text_select_row:
            filter_mold = read_mold_file(self.path_filter_dir, text_select_row)
            if filter_mold is None:
                self.filter_list_update()
                return
            else:
                self.calic_view_update(filter_mold)

        self.main_form.calicTemplateButDel.setEnabled(bool(text_select_row))
        self.main_form.calicTemplateButSeve.setEnabled(bool(text_select_row))

        # selected_items = self.main_form.calicTemplateList.selectedItems()
        # if len(selected_items) == 1:
        #     if selected_items[0].text().find('.conf') != -1:
        #         filter_mold = read_mold_file(self.path_filter_dir, selected_items[0].text())
        #         self.calic_view_update(filter_mold)

    def filter_tle_list_update(self, path_tle_dir: str = None):
        """
        Заполние таблицы с фильтрами TLE файлами
        :param path_tle_dir: Путь к директории с TLE файлами
        :return:
        """

        if path_tle_dir is None or not os.path.exists(path_tle_dir):
            return

        self.main_form.calicTLELableDate.setText(
            f"от {self.main_form.manager.get_full_tle_date().strftime('%d-%m-%Y %H:%M')}")

        self.main_form.calicTLEList.clear()

        for file in os.listdir(path_tle_dir):
            if file.split('.')[-1] == "tle" and file != "full.tle":
                item_file_tle = QListWidgetItem()
                item_file_tle.setText(file)
                self.main_form.calicTLEList.addItem(item_file_tle)
        # print("updateTleList")

    def calic_butt_tle_update(self):
        """
        Обработка нажатия кнопки: \n
        Обновление файла начальных условий
        :return:
        """

        self.main_form.show_massage_method("Обновление TLE Файла")
        self.main_form.calicTLEUpdateButt.setEnabled(False)
        self.main_form.repaint()

        self.main_form.manager.download_tle()
        self.filter_tle_list_update(self.main_form.current_config['Path']['tle_directory'])

        self.main_form.show_massage_method("")
        self.main_form.calicTLEUpdateButt.setEnabled(True)
        self.main_form.repaint()

    def calic_butt_start(self):
        """
        Обработка нажатия кнопки: \n
        Начать расчёт целеуказаний
        :return:
        """
        self.main_form.action_view.view_butt_selection_reset()

        self.filter_list_apply_or_save(current_config=self.main_form.current_config,
                                       flag_save_as_mold=False)

        if self.main_form.calicCheckClearCuDir.isChecked():
            self.main_form.manager.delete_all()

        tle_file = self.main_form.current_config["TLE"]["user_file"]
        if not tle_file:
            tle_file = self.main_form.current_config["TLE"]["default_file"]

        # self.main_form.manager.calculate(tle_file)
        # threading.Thread(target=self.main_form.manager.calculate,
        #                  args=(tle_file,)).start()
        threading.Thread(target=self.calic_process_calculate,
                         args=(tle_file,)).start()

        # print("calicStart")

    def calic_process_calculate(self, tle_file: str = None):
        """
        Функфия для запуска расчёта в отдельном потоке
        :param tle_file: Имя Tle-файла для расчёта
        :return:
        """
        if tle_file is None:
            return

        self.main_form.calicStartButt.setEnabled(False)
        self.main_form.calicStopButt.setEnabled(True)
        self.main_form.tabViewer.setEnabled(False)

        # print("Start Calic")
        self.main_form.manager.calculate(tle_file)
        self.main_form.action_view.update_ka_data()
        # print("finish Calic")

        self.main_form.calicStartButt.setEnabled(True)
        self.main_form.calicStopButt.setEnabled(False)

        self.main_form.tabViewer.setEnabled(True)

    def calic_butt_stop(self):
        """
        Обработка нажатия кнопки: \n
        Отправить сигнал об останновки расчёта
        :return:
        """
        self.main_form.manager.terminate()

    def calic_butt_clear_ang_dir(self):
        """
        Обработка нажатия кнопки: \n
        Удаление насчитанных целеуказаний
        :return:
        """
        self.main_form.manager.delete_all()
        self.main_form.action_view.update_ka_data()

    def calic_butt_filter_save(self):
        """
        Обработка нажатия кнопки: \n
        Сохранить изменения выбранного шаблона
        :return:
        """

        selected_items = self.main_form.calicTemplateList.selectedItems()
        if len(selected_items) == 1:
            if selected_items[0].text().find('.conf') != -1:
                self.filter_list_apply_or_save(selected_items[0].text())
        # print("calicButtFilterSave")

    def calic_butt_update_all_lists(self):
        """
        Обработка нажатия кнопки: \n
        Пересканировать каталоги шаблонов и Tle файлов с последующим
        обновлением списков
        :return:
        """

        # Сохранить выбранную строку таблицы с шаблонами
        selected_items_mold = self.main_form.calicTemplateList.selectedItems()
        if len(selected_items_mold) == 1:
            selected_items_mold = selected_items_mold[0].text()

        # Заполнение таблицы с шаблонами
        self.filter_list_update()

        # если был выбранный элемент выберем его повторно
        if selected_items_mold:
            selected_items_mold = self.main_form.calicTemplateList.findItems(
                selected_items_mold, Qt.MatchRegExp | Qt.MatchWildcard)
            if len(selected_items_mold):
                selected_items_mold[0].setSelected(True)

        # =======================================================================

        # Сохранить выбранную строку
        selected_items_tle = self.main_form.calicTLEList.selectedItems()
        if len(selected_items_tle) == 1:
            selected_items_tle = selected_items_tle[0].text()

        # Заполнение таблицы с TLE
        self.filter_tle_list_update(self.main_form.current_config['Path']['tle_directory'])

        # если был выбранный элемент выберем его повторно
        if selected_items_tle:
            selected_items_tle = self.main_form.calicTLEList.findItems(
                selected_items_tle, Qt.MatchRegExp | Qt.MatchWildcard)
            if len(selected_items_tle):
                selected_items_tle[0].setSelected(True)

    def calic_butt_filter_save_as(self):
        """
        Обработка нажатия кнопки: \n
        Сохранить установленный шаблон как file_name
        :return:
        """

        file_name, ok = QInputDialog.getText(self.main_form, " ", "Имя фильтра")

        if ok and bool(file_name):
            self.filter_list_apply_or_save(file_name + ".conf")
            self.filter_list_update()
        # print("calicButtFilterSaveAs")

    def calic_butt_filter_del(self):
        """
        Обработка нажатия кнопки: \n
        Удалить выбранный шаблон
        :return:
        """
        selected_items = self.main_form.calicTemplateList.selectedItems()

        if len(selected_items) != 1:
            return

        if selected_items[0].text().find('.conf') != -1:
            os.remove(os.getcwd() + "/" + self.path_filter_dir + "/" + selected_items[0].text())
            self.filter_list_update()

        # print("calicButtFilterDel")

    def calic_butt_filter_cansel(self):
        """
        Обработка нажатия кнопки: \n
        Установить последний использованный шаблон
        :return:
        """
        self.main_form.calicTemplateList.setCurrentRow(-1)
        self.calic_view_update(self.main_form.current_config)

    def calc_butt_data_time_now(self):
        """
        Обработка нажатия кнопки: \n
        Установить текущее астрономическое время для расчёта
        :return:
        """

        # d_date_time = (self.main_form.calicFilterTimeEditMin.dateTime().
        #                secsTo(self.main_form.calicFilterTimeEditMax.dateTime()))
        #
        # self.main_form.calicFilterTimeEditMin.setDate(QDate.currentDate())
        #
        # self.main_form.calicFilterTimeEditMax.setDateTime(
        #     self.main_form.calicFilterTimeEditMin.dateTime().addSecs(d_date_time)
        # )
        current_date = self.main_form.manager.get_sunrise_sunset()

        self.main_form.calicFilterTimeEditMin.setDateTime(current_date[0])
        self.main_form.calicFilterTimeEditMax.setDateTime(current_date[1])


def save_mold_to_file(filter_mold: dict[str, dict] = None,
                      path_filter_dir: str = "",
                      mold_name: str = ""):
    """
    Сохранить файл шаблона фильтрации
    :param filter_mold: Словарь с настройками
    :param path_filter_dir: путь к директории с шаблонами
    :param mold_name: имя файла шаблона
    :return:
    """
    if (filter_mold is None) or (path_filter_dir == "") or (mold_name == ""):
        return

    parser = ConfigParser(inline_comment_prefixes="#")
    parser.read_dict(filter_mold)
    file = os.path.join(os.getcwd() + "/" + path_filter_dir, mold_name)
    with open(file, 'w') as configfile:
        parser.write(configfile)


def read_mold_file(path_filter_dir: str = None, filename: str = None):
    """
    Прочитать файл шаблона фильтрации
    :param path_filter_dir: путь к директории с шаблонами
    :param filename: имя файла шаблона
    :return: Словарь с настройками
    """
    if (filename is None) or (path_filter_dir is None):
        return None

    parser = ConfigParser(inline_comment_prefixes="#")
    parser.read(os.path.join(os.getcwd() + "/" + path_filter_dir, filename))
    conf = {}
    try:
        for section in parser.sections():
            conf[section] = {}
            for key, val in parser.items(section):
                conf[section][key] = val
    except (NoSectionError, NoOptionError) as e:
        logging.error(str(e))
        return None
    return conf


class ActionView:
    """
    Клас взаимодействия с окном Анализа
    """

    def __init__(self, main_form: GuiFormMain = None):
        """
        Конструктор взаимодействий с Анализом
        :param main_form: Экземпляр главной формы
        """
        if main_form is None:
            raise ValueError("Ошибка создания ActionView")

        self.main_form = main_form
        """Главная форма"""

        # Настройка формы
        self.main_form.tabViewer.setEnabled(False)

        self.main_form.tableListKA.header().setStretchLastSection(False)
        self.main_form.tableListKA.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.main_form.tableListKA.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.main_form.tableListKA.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.main_form.tableKAInfo.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.main_form.tableKAInfo.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.main_form.buttInvertCheck.setVisible(False)
        self.main_form.buttDelNoCheck.setVisible(False)

        # Создание графиков
        self.figGraphPolar, self.axGraphPolar = self.createGraphPolar()
        self.figGraphTime, self.axGraphTime, self.ToolGraphTime = self.createGraphTime()

        # Обявление Переменных
        self.all_angs = dict()
        """Все анги из каталога"""

        self.ang_Line = dict()
        """ Словарь отрисованных фигур\n
        dict(Name_Ang : Line2D,Line2D,Line2D,Line2D,Line2D)\n
        [0]Time, [1]TimeShadow, [2]polar, [3]polarShadow \n 
        [4]polarStartDot"""

        self.ang_Line_Check = set()
        """Не нужен??? """

        self.selectAngGraph = set()
        """ Список имён выбранных ANG файлов ***.ang:str"""

        self.selectEffectsSel = [pe.Stroke(linewidth=5, foreground='magenta'), pe.Normal()]
        """"Стиль эффекта для выделенных фигур"""

        self.selectEffectsUnsel = [pe.Stroke(), pe.Normal()]
        """"Стиль эффекта для невыделенных фигур"""

        inf_label = list(zip(["Номер", "Имя", "Идентификатор", "Страна", "Запущен", "Период",
                              "Время начала", "Время конца", "Дальность", "Угол"],
                             ["OBJECT_NUMBER", "OBJECT_NAME", "OBJECT_ID", "COUNTRY", "LAUNCH", "PERIOD",
                              "TIME_START", "TIME_STOP", "MAX_DISTANS", "MAX_EVAL"]))

        self.important_inf = dict(zip(range(10), inf_label))
        """Сгенерированный словарь с для вывода информации о КА"""

        self.update_ka_data()
        # threading.Thread(target=self.updateKAData,
        #                  args=()).start()

        if len(self.all_angs):
            # self.main_form.tabWidget.setCurrentIndex(2)
            self.main_form.set_tab_view_current_index(2)

    def createGraphPolar(self) -> tuple[plt.Figure, plt.PolarAxes]:
        """
        Создание полярного графика
        :return: Поле для графика, График
        """

        fig, ax = plt.subplots(facecolor="#e5e5e5", subplot_kw={'projection': 'polar'})
        ax.set_facecolor("#e5e5e5")

        self.graph_polar_tuner(ax)

        self.main_form.layoutGraphPolar.addWidget(FigureCanvas(fig))
        self.main_form.layoutGraphPolar.itemAt(0).widget().setMinimumSize(QtCore.QSize(300, 300))
        fig.canvas.draw()
        return fig, ax

    @staticmethod
    def graph_polar_tuner(ax: plt.PolarAxes):
        """Настройка полей полярного графика"""

        ax.set_theta_zero_location("S")  # Начало север
        # ax.set_theta_direction(-1)  # Отразить
        ax.set_rlim(bottom=0, top=90, emit=1)  # Установите пределы обзора по радиальной оси
        ax.set_yticks(np.arange(0, 91, 15))  # Сетка
        ax.set_yticklabels([])
        # ax.set_yticklabels(ax.get_yticks()[::-1])
        # ax.set_rlabel_position(120)
        if True:
            labels = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE', ]
            compass = [n / float(len(labels)) * 2 * np.pi for n in range(len(labels))]
            compass += compass[:1]
            ax.set_xticks(compass[:-1], labels)

    def createGraphTime(self) -> tuple[plt.Figure, plt.Axes, NavigationToolbar]:
        """"
        Создание графика Аз/Время
        :return: Поле для графика, График, Панель управления графиком
        """

        fig, ax = plt.subplots(facecolor="#e5e5e5")
        ax.set_facecolor("#e5e5e5")
        fig.set_tight_layout(True)

        self.graph_time_tuner(ax)

        ax.format_coord = lambda x, y: 'Elevation = ' + format(y, '1.2f') + ', ' + \
                                       'Date = ' + num2date(x).strftime("%H:%M:%S\n%d/%m/%Y")

        # TO DO includ limits for zoom

        self.main_form.layoutBottGrph.addWidget(FigureCanvas(fig))
        self.main_form.layoutBottGrph.itemAt(0).widget().setMinimumSize(QtCore.QSize(0, 300))
        toolbar = NavigationToolbar(fig.canvas, self.main_form)
        self.main_form.layoutBottGrph.addWidget(toolbar)
        fig.canvas.draw()

        return fig, ax, toolbar

    @staticmethod
    def graph_time_tuner(ax: plt.Axes):
        """Настройка полей графика"""
        ax.grid(True)

        ax.set_ylabel("Elevation")

        ax.set_yticks(np.arange(0, 91, 10))
        ax.set_ylim(bottom=0, top=90, emit=1)

        # ax.set_xlabel("Time")
        # ------------------major-------------------
        ax.set_xticks(date_range(datetime.now().date(), periods=12, freq='MS'))

        major_locator = AutoDateLocator(minticks=4,
                                        # maxticks={YEARLY: 11, MONTHLY: 12, DAILY: 7,
                                        #           HOURLY: 7, MINUTELY: 10, SECONDLY: 9, MICROSECONDLY: 5}
                                        )
        ax.xaxis.set_major_locator(major_locator)

        major_formatter = ConciseDateFormatter(major_locator)
        major_formatter.formats[5] = '%Ss. '
        ax.xaxis.set_major_formatter(major_formatter)

        ax.tick_params(axis='x', which='major',
                       labelsize=14, pad=12,
                       colors='k',
                       grid_color='k')
        # ------------------minor-------------------
        # minor_locator = AutoMinorLocator(2)
        # ax.xaxis.set_minor_locator(minor_locator)
        #
        # minor_formatter = ConciseDateFormatter(minor_locator, show_offset=False)
        # minor_formatter.formats[3] = '%H:%M '  # hrs
        # minor_formatter.formats[4] = '%H:%M '  # min
        # minor_formatter.formats[5] = '%Ss. '
        # ax.xaxis.set_minor_formatter(minor_formatter)
        #
        # ax.grid(axis='x', which='minor',
        #         linewidth=1, linestyle='--',
        #         color='g', alpha=0.2)

        # ------------------old-------------------
        # ax.xaxis.set_major_locator(DayLocator())
        # ax.xaxis.set_major_formatter(DateFormatter('%d/%m/%y'))
        # ax.tick_params(axis='x', which='major',
        #                labelsize=16, pad=12,
        #                colors='r',
        #                grid_color='r')
        #
        # ax.xaxis.set_minor_locator(HourLocator())
        # ax.xaxis.set_minor_formatter(DateFormatter("%H:%M:%S"))
        # ax.tick_params(axis='x', which='minor',
        #                labelsize=8)
        # ax.grid(True)
        # ax.grid(axis='x', which='minor', linewidth=1.5,  color='g')

    def clear_KA(self, flag_clear_dir=True):
        """
        Сброс отображаемых аппаратов
        :param flag_clear_dir: очистить ANG директорию ДА/НЕТ
        :return:
        """
        # print("clear_KA")

        self.main_form.status_gui = "Очистка списка аппаратов"

        if threading.current_thread().name == "MainThread":
            self.main_form.repaint()

        if len(self.all_angs) == 0:
            return

        self.axGraphTime.cla()
        self.axGraphPolar.cla()

        self.graph_polar_tuner(self.axGraphPolar)
        self.graph_time_tuner(self.axGraphTime)

        self.ang_Line.clear()
        self.ang_Line_Check.clear()
        self.selectAngGraph.clear()

        self.figGraphPolar.canvas.draw()
        self.figGraphTime.canvas.draw()

        self.main_form.tableListKA.clear()
        self.all_angs.clear()
        if flag_clear_dir:
            # print("start clear")
            self.main_form.manager.delete_all()

        self.set_enable_button(len(self.all_angs) != 0)
        # print("finish_claer")

    def update_ka_data(self):
        """
        Отобразить ANG файлы с графиками
        :return:
        """
        # print("updateKAData")

        self.clear_KA(False)

        self.main_form.status_gui = "Получение списка аппаратов "

        self.main_form.viewButtUpdateCU.setEnabled(False)

        if threading.current_thread().name == "MainThread":
            self.main_form.repaint()

        self.all_angs = deepcopy(self.main_form.manager.get_ang_dict_with_data())

        if bool(self.all_angs):

            for norad_id in self.all_angs.keys():

                self.main_form.status_gui = (f"Построение графиков "
                                             f"{self.main_form.tableListKA.topLevelItemCount() / len(self.all_angs) * 100: .2f}%")

                if threading.current_thread().name == "MainThread":
                    self.main_form.repaint()

                itemKa = QTreeWidgetItem(self.main_form.tableListKA)
                itemKa.setFlags(itemKa.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                itemKa.setCheckState(0, Qt.Unchecked)
                itemKa.setData(0, Qt.EditRole, norad_id)

                current_sat = self.all_angs.get(norad_id)  # Получить анги

                for ang in current_sat.keys():

                    if len(current_sat) > 1:

                        itemKa.setData(1, Qt.EditRole, "...")

                        itemAng = QTreeWidgetItem(itemKa)
                        itemAng.setFlags(itemAng.flags() | Qt.ItemIsUserCheckable)
                        itemAng.setCheckState(1, Qt.Unchecked)
                        itemAng.setData(1, Qt.EditRole, ang)

                        itemKa.addChild(itemAng)

                        added_element = itemAng

                    else:
                        # print()
                        itemKa.setData(1, Qt.EditRole, ang)
                        # itemKa.setCheckState(1, Qt.Unchecked)
                        itemKa.setTextAlignment(1, Qt.AlignHCenter | Qt.AlignVCenter)

                        added_element = itemKa

                    d = current_sat.get(ang)
                    # --------Отрисовка на графиках---------

                    # df_shine = d[d["Ph"] != 0.0]
                    # df_shadow = d[d["Ph"] == 0.0]

                    df_shine = d.copy(deep=True)
                    df_shine['Az'] = np.deg2rad(df_shine['Az'].values)
                    df_shine.loc[df_shine["Ph"] == 0, 'Time'] = NaT
                    df_shine.loc[df_shine["Ph"] == 0, 'Az'] = np.nan

                    df_shadow = d.copy(deep=True)
                    df_shadow['Az'] = np.deg2rad(df_shadow['Az'].values)
                    df_shadow.loc[df_shadow["Ph"] != 0, 'Time'] = NaT
                    df_shadow.loc[df_shadow["Ph"] != 0, 'Az'] = np.nan

                    self.ang_Line[ang] = [
                        self.axGraphTime.plot(df_shine.Time.values, df_shine.Elev.values, linewidth=2, )[0],
                        self.axGraphTime.plot(df_shadow.Time.values, df_shadow.Elev.values,
                                              linewidth=1, color="white")[0],
                        # linewidth= 1, color="grey", marker='.' , markersize = 1)[0],

                        self.axGraphPolar.plot(df_shine.Az.values,
                                               90 - df_shine.Elev.values,
                                               visible=False, linewidth=2)[0],
                        self.axGraphPolar.plot(df_shadow.Az.values,
                                               90 - df_shadow.Elev.values,
                                               visible=False, linewidth=1, color="white")[0],
                        # visible = False, linewidth = 1, color = "grey", marker = '.', markersize = 1)[0]

                        self.axGraphPolar.plot(np.deg2rad(d.Az.values[0]), 90 - d.Elev.values[0],
                                               'o', visible=False, markersize=4)[0]
                    ]

                    self.ang_Line[ang][2].set_color(self.ang_Line[ang][0].get_color())
                    self.ang_Line[ang][4].set_color(self.ang_Line[ang][0].get_color())

                    if added_element is not None:
                        added_element.setBackground(2,
                                                    # QColor(self.ang_Line[ang][0].get_color() if
                                                    #        len(df_shine) != 0
                                                    #        else Qt.white))
                                                    QBrush(QColor(self.ang_Line[ang][0].get_color()),
                                                           # Qt.SolidPattern if len(df_shine) != 0 else Qt.Dense2Pattern))
                                                           Qt.SolidPattern if df_shine.Time.notna().sum() != 0 else Qt.Dense2Pattern))

                    # ========================================
                # self.tableListKA.addTopLevelItem(itemKa);

            self.main_form.status_gui = "Отрисовка графиков"
            if threading.current_thread().name == "MainThread":
                self.main_form.repaint()

            self.figGraphPolar.tight_layout()
            self.figGraphPolar.canvas.draw()
            self.figGraphTime.tight_layout()
            self.figGraphTime.canvas.draw()
            self.ToolGraphTime.update()
        else:
            sleep(0.1)
            self.main_form.set_tab_view_current_index(1)
            self.main_form.tabViewer.setEnabled(True)
            print("amgs_isEmpty")

        self.main_form.status_gui = ""

        self.main_form.viewButtUpdateCU.setEnabled(True)

        self.set_enable_button(len(self.all_angs) != 0)

        self.main_form.tableListKA.resizeColumnToContents(2)

        self.main_form.tabViewer.setEnabled(True)

        self.main_form.status_gui = ""

    def set_enable_button(self, state_enable: bool = False):
        """
        Установить доступность кнопок управления окна
        :param state_enable: доступность кнопок
        :return:
        """
        self.main_form.calicClearAngDirButt.setEnabled(state_enable)
        self.main_form.buttResetSelection.setEnabled(state_enable)
        self.main_form.buttOnlyCheck.setEnabled(state_enable)
        self.main_form.viewButtCliarCU.setEnabled(state_enable)
        self.main_form.viewButtMoveCU.setEnabled(state_enable)
        self.main_form.viewButtSieve.setEnabled(state_enable)

    def fillKaInfo(self, id_ka: int, ang_name: str):
        """
        Вывод информации о КА и уточнение из ANG
        :param id_ka: NORAD КА
        :param ang_name: имя ANG файла
        :return:
        """
        # print("fillKaInfo")

        dataKA = self.main_form.manager.get_sat_info(id_ka)

        data_ang = dict()

        if ang_name.endswith('.ang'):
            data_ang = self.get_ang_info(id_ka, ang_name)

        for idInf, titleInf in self.important_inf.items():
            # Информация об КА
            if (idInf > 5 and
                    not ang_name.endswith('.ang')):
                break

            self.main_form.tableKAInfo.insertRow(idInf)

            item_label = QTableWidgetItem()
            item_label.setData(Qt.EditRole, titleInf[0])
            self.main_form.tableKAInfo.setItem(idInf, 0, item_label)

            # Информация об орбите
            item_inf = QTableWidgetItem()
            if idInf <= 5:
                item_inf.setData(Qt.EditRole, str(dataKA[titleInf[1]].values[0]))
            else:
                item_inf.setData(Qt.EditRole, str(data_ang[titleInf[1]]))

            self.main_form.tableKAInfo.setItem(idInf, 1, item_inf)

    def get_ang_info(self, id_ka: int, ang_name: str) -> dict:
        """
        Получит информацию по ANG файлу
        :param id_ka: номер КА
        :param ang_name: Имя файла с проходом
        :return: dict("TIME_START":str, "TIME_STOP":str, "MAX_DISTANS":str, "MAX_EVAL:str")
        """
        data_ang = dict()
        data_ang.update({"TIME_START": self.all_angs[id_ka][ang_name]["Time"].min().strftime('%d-%m-%Y %H:%M')})
        data_ang.update({"TIME_STOP": self.all_angs[id_ka][ang_name]["Time"].max().strftime('%d-%m-%Y %H:%M')})
        data_ang.update({"MAX_DISTANS": f"{self.all_angs[id_ka][ang_name].Distance.max() / 1000:.2f} Км."})
        data_ang.update({"MAX_EVAL": f"{self.all_angs[id_ka][ang_name].Elev.max():.2f}°"})
        return data_ang

    def slotSelectKaList(self):
        """
        Обработка события выделения строк
        :return:
        """

        selectedColumns = self.main_form.tableListKA.selectedItems()
        """Список выделенных строк:list[QTreeWidgetItem]"""

        if len(selectedColumns) == 0:
            self.view_butt_selection_reset()
            return

        # Сделать все фигуры на графике прозрачными
        if not self.selectAngGraph:  # нет выбранных
            for keyLines in self.ang_Line_Check if bool(self.ang_Line_Check) else self.ang_Line.keys():
                self.ang_Line[keyLines][0].set(lw=2, alpha=0.2, path_effects=[pe.Stroke(), pe.Normal()])
                self.ang_Line[keyLines][1].set(lw=1, alpha=0.2, path_effects=[pe.Stroke(), pe.Normal()])

        newSelectAng = set()
        """Выделенные впервые"""

        # Очистить таблицу информации о КА
        self.main_form.tableKAInfo.clear()

        # Заполнение информации
        if len(selectedColumns) == 1:
            # Получить номер КА
            idKA: int = (int(selectedColumns[0].data(0, Qt.EditRole)  # если родителя нет
                             if (selectedColumns[0].parent() is None)
                             else selectedColumns[0].parent().data(0, Qt.EditRole)))  # если родитель есть

            # Получить имя ANG файла
            ang_name: str = selectedColumns[0].data(1, Qt.EditRole)

            self.fillKaInfo(idKA, ang_name)

        # ===========================
        # Selected New
        for item in selectedColumns:

            # Проверка выделен ли ANG
            if item.data(1, Qt.EditRole) in self.selectAngGraph:
                newSelectAng.add(item.data(1, Qt.EditRole))
                continue  # Если ANG уже выделен

            if item.childCount() == 0:
                # Если КА имеет 1 ANG
                newSelectAng.add(
                    self.selectGraph(item.data(1, Qt.EditRole))
                )

            else:
                # Если КА имеет >1 ANG
                for childIndex in range(item.childCount()):  # проход по вложенным
                    newSelectAng.add(
                        self.selectGraph(item.child(childIndex).data(1, Qt.EditRole))
                    )

        # ===========================
        #   Unselected old
        # Проход по строкам с которых сняли выделение
        for item in self.selectAngGraph - newSelectAng:
            self.selectAngGraph.discard(
                self.selectGraph(item, True)
            )

        # Добавление впервые выделенных в список выделенных
        self.selectAngGraph.update(newSelectAng)

        # print('repaint time: ', time.time() - start_time)

        # Перерисовка графиков (Самая долгая)
        self.figGraphPolar.canvas.draw()
        self.figGraphPolar.canvas.flush_events()
        self.figGraphTime.canvas.draw()
        self.figGraphTime.canvas.flush_events()
        self.main_form.repaint()

        # print('end time: ', time.time() - start_time)
        # print("\n")

    def selectGraph(self, angName: str, unselection: bool = False) -> str:
        """
        Функция выделения фигур на графиках

        :param angName: имя Ang Файла для взаимодействия
        :param unselection:
        :return: имя Ang Файла
        """

        if not self.ang_Line:
            return ''

        self.ang_Line[angName][0].set(lw=3, zorder=2 if unselection else 3,
                                      alpha=0.1 if unselection else 1,
                                      path_effects=self.selectEffectsUnsel if
                                      unselection else
                                      self.selectEffectsSel)
        self.ang_Line[angName][1].set(lw=2, zorder=2 if unselection else 3,
                                      alpha=0.1 if unselection else 1,
                                      path_effects=self.selectEffectsUnsel if
                                      unselection else
                                      self.selectEffectsSel)
        self.ang_Line[angName][2].set_visible(not unselection)
        self.ang_Line[angName][3].set_visible(not unselection)
        self.ang_Line[angName][4].set_visible(not unselection)

        return angName

    def view_butt_selection_reset(self):
        """
        Обработка нажатия кнопки: \n
        Сброс выбора
        """
        if self.main_form.tableListKA.topLevelItemCount() == 0:
            return

        self.main_form.tableListKA.clearSelection()

        for item in self.selectAngGraph:
            self.selectGraph(item, True)
        self.selectAngGraph.clear()

        if len(self.selectAngGraph) == 0:  # нет выбранных
            for keyLines in self.ang_Line_Check if bool(self.ang_Line_Check) else self.ang_Line.keys():
                self.ang_Line[keyLines][0].set(lw=2, alpha=1, path_effects=[pe.Stroke(), pe.Normal()])
                self.ang_Line[keyLines][1].set(lw=1, alpha=1, path_effects=[pe.Stroke(), pe.Normal()])

        self.figGraphPolar.canvas.draw()
        self.figGraphTime.canvas.draw()

    def view_butt_show_only_marked(self, check_state: bool = True):
        """
        Обработка нажатия кнопки: \n
        Отобразить только выделенные?
        :param check_state: Отобразить только выделенные Да/Нет:
        """
        if len(self.all_angs) == 0:
            return

        for angSet in self.ang_Line.values():
            angSet[0].set_visible(not check_state)
            angSet[1].set_visible(not check_state)

        for itemKA in self.main_form.tableListKA.findItems("*", Qt.MatchRegExp | Qt.MatchWildcard, 0):

            invisible = (itemKA.checkState(0) == Qt.Unchecked
                         and itemKA.checkState(1) == Qt.Unchecked
                         and check_state)
            itemKA.setHidden(invisible)

            if check_state and itemKA.childCount() == 0:
                angName = itemKA.data(1, Qt.EditRole)
                self.ang_Line[angName][0].set_visible(not invisible)
                self.ang_Line[angName][1].set_visible(not invisible)

            for childIndex in range(itemKA.childCount()):  # проход по вложенным
                invisible = (itemKA.child(childIndex).checkState(1) != Qt.Checked
                             and check_state)
                itemKA.child(childIndex).setHidden(invisible)

                angName = itemKA.child(childIndex).data(1, Qt.EditRole)
                self.ang_Line[angName][0].set_visible(not invisible)
                self.ang_Line[angName][1].set_visible(not invisible)

        self.figGraphPolar.canvas.draw()
        self.figGraphTime.canvas.draw()

    def view_butt_move_cu(self):
        """
        Обработка нажатия кнопки: \n
        Копирование целеуказаний в новую папку
        :return:
        """

        if len(self.all_angs) == 0:
            return

        self.main_form.show_massage_method("Копирование данных")
        self.main_form.viewButtMoveCU.setEnabled(False)
        self.main_form.repaint()

        path = QFileDialog.getExistingDirectory(self.main_form,
                                                "Копировать",
                                                os.getcwd(),
                                                QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog
                                                )
        if path:
            self.main_form.manager.copy_ang_to_dst(path)

        self.main_form.viewButtMoveCU.setEnabled(True)
        self.main_form.show_massage_method("")

        # print("moveAng")

    def view_butt_sieve(self):
        """
        Обработка нажатия кнопки: \n
        Прореживание
        """

        if len(self.all_angs) == 0:
            return

        self.main_form.show_massage_method("Прореживание данных")
        self.main_form.viewButtSieve.setEnabled(False)
        self.main_form.manager.thin_out(self.main_form.viewButtSieveEdit.value())
        self.update_ka_data()
        self.main_form.viewButtSieve.setEnabled(True)
        self.main_form.show_massage_method("")
