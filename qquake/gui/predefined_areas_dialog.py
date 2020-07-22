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
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QDialogButtonBox,
    QListWidgetItem
)

from qgis.gui import QgsGui

from qquake.gui.gui_utils import GuiUtils
from qquake.services import SERVICE_MANAGER

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('predefined_areas_widget_base.ui'))


class PredefinedAreasWidget(QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)

        for name in SERVICE_MANAGER.available_predefined_bounding_boxes():
            extent = SERVICE_MANAGER.predefined_bounding_box(name)
            item = QListWidgetItem(extent['title'])
            item.setData(Qt.UserRole, name)
            item.setData(Qt.UserRole+1, True)  # read only
            self.region_list.addItem(item)

        self.region_list.currentItemChanged.connect(self._item_changed)

    def _item_changed(self, current, previous):
        name = current.data(Qt.UserRole)
        extent = SERVICE_MANAGER.predefined_bounding_box(name)

        self.edit_label.setText(extent['title'])
        self.spin_min_long.setValue(extent['boundingbox'][0])
        self.spin_max_long.setValue(extent['boundingbox'][2])
        self.spin_min_lat.setValue(extent['boundingbox'][1])
        self.spin_max_lat.setValue(extent['boundingbox'][3])

        read_only = current.data(Qt.UserRole+1)
        for w in [self.edit_label, self.spin_min_long, self.spin_max_long, self.spin_min_lat, self.spin_max_lat]:
            w.setEnabled(not read_only)
        

class PredefinedAreasDialog(QDialog):

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)

        self.setWindowTitle(self.tr('Customize Areas'))

        QgsGui.enableAutoGeometryRestore(self)

        self.widget = PredefinedAreasWidget()
        l = QVBoxLayout()
        l.addWidget(self.widget)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        l.addWidget(self.button_box)
        self.setLayout(l)
