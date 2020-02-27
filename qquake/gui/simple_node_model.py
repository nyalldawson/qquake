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

from qgis.PyQt.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    Qt
)
from qgis.PyQt.QtGui import QFont


class ModelNode:

    def __init__(self, data, checked=None):
        self._data = data
        self._column_count = len(self._data)
        self._children = []
        self._parent = None
        self._row = 0
        self._checked = checked

    def data(self, column):
        if 0 <= column < len(self._data):
            return self._data[column]
        return None

    def columnCount(self):
        return self._column_count

    def childCount(self):
        return len(self._children)

    def checkable(self):
        return self._checked is not None

    def checked(self):
        return self._checked

    def setChecked(self, checked):
        self._checked = checked

    def child(self, row):
        if 0 <= row < self.childCount():
            return self._children[row]

        return None

    def parent(self):
        return self._parent

    def row(self):
        return self._row

    def show_bold(self):
        return bool(self._children)

    def addChild(self, child):
        child._parent = self
        child._row = len(self._children)
        self._children.append(child)
        self._column_count = max(child.columnCount(), self._column_count)


class SimpleNodeModel(QAbstractItemModel):

    def __init__(self, nodes, headers=None):
        super().__init__()
        self._root = ModelNode([None])
        for node in nodes:
            self._root.addChild(node)
        self.headers = headers or []

    def rowCount(self, index):
        if index.isValid():
            return index.internalPointer().childCount()
        return self._root.childCount()

    def addChild(self, node, _parent):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()
        parent.addChild(node)

    def index(self, row, column, _parent=None):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()

        if not super().hasIndex(row, column, _parent):
            return QModelIndex()

        child = parent.child(row)
        if child:
            return super().createIndex(row, column, child)
        else:
            return QModelIndex()

    def parent(self, index):
        if index.isValid():
            p = index.internalPointer().parent()
            if p:
                return super().createIndex(p.row(), 0, p)
        return QModelIndex()

    def columnCount(self, index):
        if index.isValid():
            return index.internalPointer().columnCount()
        return self._root.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()

        if node.checkable() and index.column() == 0:
            if role == Qt.CheckStateRole:
                return Qt.Checked if node.checked() else Qt.Unchecked
            return None
        else:
            if role == Qt.DisplayRole:
                return node.data(index.column())
            elif role == Qt.FontRole and node.show_bold():
                f = QFont()
                f.setBold(True)
                return f
        return None

    def setData(self, index, value, role):
        if not index.isValid():
            return None
        node = index.internalPointer()

        if node.checkable() and index.column() == 0:
            node.setChecked(value)
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True

        return False

    def flags(self, index):
        f = super().flags(index)

        node = index.internalPointer()
        if node.checkable() and index.column() == 0:
            f = f | Qt.ItemIsUserCheckable
        return f

    def headerData(self, section, orientation, role):
        if self.headers and orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return super().headerData(section, orientation, role)
