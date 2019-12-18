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

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import (
    Qt,
    QDate,
    QVariant
)
from qgis.core import (
        QgsVectorLayer,
        QgsField,
        QgsFields,
        QgsFeature,
        QgsGeometry,
        QgsPointXY,
        QgsProject,
        QgsWkbTypes,
        QgsRectangle,
        QgsCoordinateReferenceSystem
)

from qgis.gui import (
        QgsRubberBand,
        QgsMapCanvas
)

from .qquake_defs import (
        fdsn_events_capabilities,
        fdsn_event_fields,
        getFDSNEvent,
)

import csv
import urllib.request
from collections import defaultdict

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'qquake_dialog_base.ui'))

MAX_LON_LAT = [-180,-90,180,90]

class QQuakeDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(QQuakeDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.iface = iface

        # QgsExtentGroupBox utilities to se tup in the init
        self.mExtentGroupBox.setMapCanvas(self.iface.mapCanvas())
        self.mExtentGroupBox.setCurrentExtent(self.iface.mapCanvas().extent(), self.iface.mapCanvas().mapSettings().destinationCrs())
        self.mExtentGroupBox.setOriginalExtent(QgsRectangle(*MAX_LON_LAT), QgsCoordinateReferenceSystem(4326))
        self.mExtentGroupBox.setOutputCrs(QgsCoordinateReferenceSystem(4326))

        # connect the date chaning to the refreshing function
        self.fdsn_event_start_date.dateChanged.connect(self.refreshDate)

        # fill the FDSN combobox with the dictionary keys
        self.fdsn_event_ws_combobox.addItems(fdsn_events_capabilities.keys())

        # connect to refreshing function to refresh the UI depending on the WS
        self.refreshWidgets()

        # change the UI parameter according to the web service chosen
        self.fdsn_event_ws_combobox.currentIndexChanged.connect(self.refreshWidgets)

        self.button_box.accepted.connect(self._getEventList)

    def refreshDate(self):
        '''
        Avoids negative date internvals bu checking start_date > end_date
        '''
        if self.fdsn_event_start_date.dateTime() > self.fdsn_event_end_date.dateTime():
            self.fdsn_event_end_date.setDate(self.fdsn_event_start_date.date())

    def refreshWidgets(self):
        '''
        Refreshing the FDSN-Event UI depending on the WS chosen
        '''

        # set DateTime Widget START according to the combobox choice
        self.fdsn_event_start_date.setMinimumDate(
            fdsn_events_capabilities[self.fdsn_event_ws_combobox.currentText()]['mindate']
        )
        self.fdsn_event_start_date.setMaximumDate(
            fdsn_events_capabilities[self.fdsn_event_ws_combobox.currentText()]['maxdate']
        )
        self.fdsn_event_start_date.setDate(
            fdsn_events_capabilities[self.fdsn_event_ws_combobox.currentText()]['defaultdate']
        )

        # set DateTime Widget END according to the combobox choice
        self.fdsn_event_end_date.setMinimumDate(
            fdsn_events_capabilities[self.fdsn_event_ws_combobox.currentText()]['mindate']
        )
        self.fdsn_event_end_date.setMaximumDate(
            fdsn_events_capabilities[self.fdsn_event_ws_combobox.currentText()]['maxdate']
        )
        # just make a week difference from START date
        self.fdsn_event_end_date.setDate(
            fdsn_events_capabilities[self.fdsn_event_ws_combobox.currentText()]['defaultdate'].addDays(-7)
        )


    def _getEventList(self):
        '''
        read the event URL and convert the response in a list
        '''

        # create the initial string depending on the WS chosen in the comobobox
        cap = fdsn_events_capabilities[self.fdsn_event_ws_combobox.currentText()]['ws']
        fdsn_event_text = fdsn_events_capabilities[self.fdsn_event_ws_combobox.currentText()]['ws']

        # append to the string the parameter of the UI (starttime, endtime, etc)
        fdsn_event_text += 'starttime={}&endtime={}&minmag={}&maxmag={}'.format(
            self.fdsn_event_start_date.dateTime().toString(Qt.ISODate),
            self.fdsn_event_end_date.dateTime().toString(Qt.ISODate),
            self.fdsn_event_min_magnitude.value(),
            self.fdsn_event_max_magnitude.value()
        )

        if self.mExtentGroupBox.isChecked():
            ext = self.mExtentGroupBox.outputExtent()
            fdsn_event_text += '&minlat={ymin}&maxlat={ymax}&minlon={xmin}&maxlon={xmax}'.format(
                ymin = ext.yMinimum(),
                ymax = ext.yMaximum(),
                xmin = ext.xMinimum(),
                xmax = ext.xMaximum()
            )

        fdsn_event_text += '&limit=1000&format=text'

        self.lineEdit.setText(fdsn_event_text)

        fdsn_event_dict = getFDSNEvent(fdsn_event_text)

        # define QgsVectorLayer to add to the map
        vl = QgsVectorLayer('Point?crs=EPSG:4326', 'mem', 'memory')

        # define and write QgsFields and get types from dictionary
        fields = QgsFields()
        for k, v in fdsn_event_fields.items():
            fields.append(QgsField(k, v))
        vl.dataProvider().addAttributes(fields)
        vl.updateFields()

        # write QgsFeatures of the FDSN Events
        lid = []
        for i in list(zip(*fdsn_event_dict.values())):

            lid.append('{}eventid={}&includeallorigins=true&includeallmagnitudes=true&format=xml'.format(
                cap,
                i[0])
            )
            feat = QgsFeature(vl.fields())
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(i[3]), float(i[2]))))
            feat.setAttributes(list(i))
            vl.dataProvider().addFeatures([feat])


        # add the layer to the map
        print(lid)
        QgsProject.instance().addMapLayer(vl)


    def checkstate(self):
        if self.mExtentGroupBox.isChecked():
            ext = self.mExtentGroupBox.outputExtent()
            print(ext.xMinimum())
            print(ext.yMaximum())
            print(ext.xMaximum())
            print(ext.yMinimum())

        else:
            print('nononono')
