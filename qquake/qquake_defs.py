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

from qgis.PyQt.QtCore import QDate

NOW = QDate.currentDate()
MAX_LON_LAT = [-180, -90, 180, 90]

# define the capabilities of each fdsn-event web service
fdsn_events_capabilities = {
    'AHEAD/SHEEC': {
        'ws': 'https://www.emidius.eu/fdsnws/event/1/query?',
        'mindate': QDate(1000, 1, 1),
        'maxdate': QDate(1899, 12, 31),
        'defaultdate': QDate(1000, 1, 1),
    },
    'INGV ASMI/CPTI': {
        'ws': 'https://emidius.mi.ingv.it/fdsnws/event/1/query?',
        'mindate': QDate(1000, 1, 1),
        'maxdate': QDate(2014, 12, 31),
        'defaultdate': NOW,
    },
    'INGV ONT/ISIDe': {
        'ws': 'http://webservices.ingv.it/fdsnws/event/1/query?',
        'mindate': QDate(1985, 1, 1),
        'maxdate': NOW,
        'defaultdate': NOW,
    },
    'ETHZ SED': {
        'ws': 'http://arclink.ethz.ch/fdsnws/event/1/query?',
        'mindate': QDate(1000, 1, 1),
        'maxdate': NOW,
        'defaultdate': NOW,
    },
    'EMSC-CSEM': {
        'ws': 'http://www.seismicportal.eu/fdsnws/event/1/query?',
        'mindate': QDate(1998, 1, 1),
        'maxdate': NOW,
        'defaultdate': NOW,
    },
    'ORFEUS ESM': {
        'ws': 'http://esm.mi.ingv.it/fdsnws/event/1/query?',
        'mindate': QDate(1950, 1, 1),
        'maxdate': NOW,
        'defaultdate': NOW,
    },
    'ISC': {
        'ws': 'http://www.isc.ac.uk/fdsnws/event/1/query?',
        'mindate': QDate(1900, 1, 1),
        'maxdate': NOW,
        'defaultdate': NOW,
    },
    'ISC (IRIS mirror)': {
        'ws': 'http://isc-mirror.iris.washington.edu/fdsnws/event/1/query?',
        'mindate': QDate(1900, 1, 1),
        'maxdate': NOW,
        'defaultdate': NOW,
    },
    'IRIS': {
        'ws': 'http://service.iris.edu/fdsnws/event/1/query?',
        'mindate': QDate(1960, 1, 1),
        'maxdate': NOW,
        'defaultdate': NOW,
    },
    'USGS': {
        'ws': 'http://earthquake.usgs.gov/fdsnws/event/1/query?',
        'mindate': QDate(1000, 1, 1),
        'maxdate': NOW,
        'defaultdate': NOW,
    },
    'NCEDC': {
        'ws': 'http://service.ncedc.org/fdsnws/event/1/query?',
        'mindate': QDate(1000, 1, 1),
        'maxdate': NOW,
        'defaultdate': NOW,
    },
    'SCEDC': {
        'ws': 'http://service.scedc.caltech.edu/fdsnws/event/1/query?',
        'mindate': QDate(1000, 1, 1),
        'maxdate': NOW,
        'defaultdate': NOW,
    }
}
