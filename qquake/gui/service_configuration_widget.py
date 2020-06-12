# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QQuakeDialog
                                 A QGIS plugin
 QQuake plugin to download seismologic data
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-11-20
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Faunalia
        email                : matteo.ghetta@faunalia.eu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from copy import deepcopy
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QDialogButtonBox,
    QCheckBox,
    QSpinBox
)
from qgis.PyQt.QtCore import QDateTime, Qt, pyqtSignal

from qgis.core import (
    Qgis,
)
from qgis.gui import (
    QgsGui,
)

from qquake.gui.gui_utils import GuiUtils
from qquake.services import SERVICE_MANAGER

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('service_configuration_widget_base.ui'))


class ServiceConfigurationWidget(QWidget, FORM_CLASS):
    WIDGET_MAP = {
        'queryeventid': 'check_filter_by_eventid',
        'queryoriginid': 'check_filter_by_originid',
        'querymagnitudeid': 'check_filter_by_magnitudeid',
        'queryfocalmechanismid': 'check_filter_by_focalmechanismid',
        'queryupdatedafter': 'check_filter_data_updated_after',
        'querycatalog': 'check_filter_by_catalog',
        'querycontributor': 'check_filter_by_contributor',
        'querycontributorid': 'check_filter_by_contributorid',
        'queryeventtype': 'check_filter_by_event_type',
        'querymagnitudetype': 'check_filter_by_magnitude_type',
        'queryincludeallorigins': 'check_can_include_all_origins',
        'queryincludeallmagnitudes': 'check_can_include_all_magnitudes',
        'queryincludearrivals': 'check_can_include_arrivals',
        'queryincludeallstationsmagnitudes': 'check_can_include_all_stations_magnitudes',
        'querylimit': 'check_has_limit_of_entries',
        'querylimitmaxentries': 'spin_has_limit_of_entries',
        'querycircular': 'check_can_filter_using_circular_area',
        'querycircularradiuskm': 'check_radius_of_circular_area_is_specified_in_km',
        'querydepth': 'check_can_filter_by_depth',
        'outputtext': 'check_can_output_text',
        'outputxml': 'check_can_output_xml',
        'outputgeojson': 'check_can_output_geojson',
        'outputjson': 'check_can_output_json',
        'outputkml': 'check_can_output_kml',
        'outputxlsx': 'check_can_output_microsoft_xlsx'
    }

    validChanged = pyqtSignal(bool)

    def __init__(self, iface, service_type, service_id, parent=None):
        """Constructor."""
        super().__init__(parent)

        self.setupUi(self)

        self.service_type = service_type
        self.service_id = service_id

        self.start_date_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")

        if service_id in SERVICE_MANAGER.available_services(service_type):
            config = SERVICE_MANAGER.service_details(service_type, service_id)
        else:
            config = {}
        self.set_state_from_config(config)

        self.title_edit.textChanged.connect(self._changed)
        self.web_service_url_edit.textChanged.connect(self._changed)

        self.combo_http_code_nodata.addItem('204', '204')

        for _, w in self.WIDGET_MAP.items():
            widget = getattr(self, w)
            if isinstance(widget, QCheckBox):
                widget.toggled.connect(self._changed)
            elif isinstance(widget, QSpinBox):
                widget.valueChanged.connect(self._changed)
        self.check_http_code_nodata.toggled.connect(self._changed)
        self.combo_http_code_nodata.currentIndexChanged.connect(self._changed)

        self._changed()

    def _changed(self):

        self.combo_http_code_nodata.setEnabled(self.check_http_code_nodata.isChecked())
        self.spin_has_limit_of_entries.setEnabled(self.check_has_limit_of_entries.isChecked())
        self.check_radius_of_circular_area_is_specified_in_km.setEnabled(self.check_can_filter_using_circular_area.isChecked())

        res, reason = self.is_valid()
        if not res:
            self.message_bar.clearWidgets()
            self.message_bar.pushMessage('', reason, Qgis.Warning, 0)
            self.validChanged.emit(False)
        else:
            self.message_bar.clearWidgets()
            self.validChanged.emit(True)

    def is_valid(self):
        if not self.title_edit.text():
            return False, self.tr('A title must be entered')

        if not self.web_service_url_edit.text():
            return False, self.tr('The web service URL must be entered')

        return True, None

    def set_state_from_config(self, config):
        self.title_edit.setText(config.get('title'))
        self.info_edit.setText(config.get('info'))
        self.info_url_edit.setText(config.get('infourl'))
        self.webservice_manual_url_edit.setText(config.get('manualurl'))
        self.data_license_edit.setText(config.get('datalicense'))
        self.data_license_url_edit.setText(config.get('datalicenseurl'))
        self.data_provider_edit.setText(config.get('dataprovider'))
        self.data_provider_url_edit.setText(config.get('dataproviderurl'))
        self.web_service_url_edit.setText(config.get('endpointurl'))
        self.qml_style_url_edit.setText(config.get('styleurl'))

        if config.get('datestart'):
            self.start_date_edit.setDateTime(QDateTime.fromString(config.get('datestart'), Qt.ISODate))
        else:
            self.start_date_edit.clear()

        if config.get('dateend'):
            self.end_date_edit.setDateTime(QDateTime.fromString(config.get('dateend'), Qt.ISODate))
        else:
            self.end_date_edit.clear()

        extent = config.get('boundingbox')
        if extent:
            self.min_lat_spin.setValue(extent[1])
            self.max_lat_spin.setValue(extent[3])
            self.min_long_spin.setValue(extent[0])
            self.max_long_spin.setValue(extent[2])
        else:
            self.min_lat_spin.setValue(-90)
            self.max_lat_spin.setValue(90)
            self.min_long_spin.setValue(-180)
            self.max_long_spin.setValue(180)

        for key, w in self.WIDGET_MAP.items():
            widget = getattr(self, w)
            if isinstance(widget, QCheckBox):
                widget.setChecked(config.get('settings', {}).get(key, False))
            elif isinstance(widget, QSpinBox):
                if key in config.get('settings', {}):
                    widget.setValue(int(config.get('settings', {}).get(key)))

        self.check_http_code_nodata.setChecked('httpcodenodata' in config.get('settings', {}))
        self.combo_http_code_nodata.setCurrentIndex(self.combo_http_code_nodata.findData(config.get('settings', {}).get('httpcodenodata', '204')))

    def get_config(self):
        if self.service_id in SERVICE_MANAGER.available_services(self.service_type):
            config = deepcopy(SERVICE_MANAGER.service_details(self.service_type, self.service_id))
        else:
            config = {
                'default': {},
                'settings': {}
            }

        config['title'] = self.title_edit.text()
        config['info'] = self.info_edit.text()
        config['infourl'] = self.info_url_edit.text()
        config['manualurl'] = self.webservice_manual_url_edit.text()
        config['datalicense'] = self.data_license_edit.text()
        config['datalicenseurl'] = self.data_license_url_edit.text()
        config['dataprovider'] = self.data_provider_edit.text()
        config['dataproviderurl'] = self.data_provider_url_edit.text()
        config['endpointurl'] = self.web_service_url_edit.text()
        config['styleurl'] = self.qml_style_url_edit.text()

        if self.start_date_edit.dateTime().isValid():
            config['datestart'] = self.start_date_edit.dateTime().toString(Qt.ISODate)
        else:
            config['datestart'] = ''

        if self.end_date_edit.dateTime().isValid():
            config['dateend'] = self.end_date_edit.dateTime().toString(Qt.ISODate)
        else:
            config['dateend'] = ''

        bounding_box = [self.min_long_spin.value(),
                        self.min_lat_spin.value(),
                        self.max_long_spin.value(),
                        self.max_lat_spin.value()]
        config['boundingbox'] = bounding_box

        settings = {}
        for key, w in self.WIDGET_MAP.items():
            widget = getattr(self, w)
            if isinstance(widget, QCheckBox):
                settings[key] = widget.isChecked()
            elif isinstance(widget, QSpinBox):
                settings[key] = widget.value()

        if self.check_http_code_nodata.isChecked():
            settings['httpcodenodata'] = self.combo_http_code_nodata.currentData()

        config['settings'] = settings

        return config

    def save_changes(self):
        config = self.get_config()
        SERVICE_MANAGER.save_service(self.service_type, self.service_id, config)


class ServiceConfigurationDialog(QDialog):

    def __init__(self, iface, service_type, service_id, parent):
        super().__init__(parent)
        self.setObjectName('ServiceConfigurationDialog')

        QgsGui.enableAutoGeometryRestore(self)

        self.setWindowTitle(self.tr('Edit Service {}').format(service_id))

        self.config_widget = ServiceConfigurationWidget(iface, service_type, service_id)
        layout = QVBoxLayout()
        layout.addWidget(self.config_widget, 1)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)
        self.config_widget.validChanged.connect(self.valid_changed)
        self.valid_changed(self.config_widget.is_valid()[0])

    def valid_changed(self, is_valid):
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(is_valid)

    def accept(self):
        self.config_widget.save_changes()
        super().accept()
