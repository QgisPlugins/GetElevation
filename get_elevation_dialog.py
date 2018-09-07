# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GetElevationDialog
                                 A QGIS plugin
 Plugin Qgis 3.0 para obtenção de dados de elevação da API Google Maps.
                             -------------------
        begin                : 2018-08-31
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Rodrigo Sousa
        email                : rodrigofrcs@hotmail.com
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


from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
import sys
import re
from PyQt4 import QtCore, QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'get_elevation_dialog_base.ui'))


class GetElevationDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(GetElevationDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.input_mode_default()
        self.outputSelectFileName.clicked.connect(self.browseSaveOutput)
        self.layerInputMode.toggled.connect(self.radio_input_layer)
        self.extentInputMode.toggled.connect(self.radio_input_extent)
        self.fileOutput.toggled.connect(self.radio_output)
        self.getExtent.clicked.connect(self.get_extent)
        self.oldPath = ''

    ###################
    #INPUT
    ###################

    def input_mode_default(self):
        self.labelLayer.setVisible(True)
        self.layersInput.setVisible(True)
        self.labelExtent.setVisible(False)
        self.labelExtentN.setVisible(False)
        self.labelExtentS.setVisible(False)
        self.labelExtentL.setVisible(False)
        self.labelExtentW.setVisible(False)
        self.labelExtentInterval.setVisible(False)
        self.extentInputInterval.setVisible(False)
        self.extentInputN.setVisible(False)
        self.extentInputS.setVisible(False)
        self.extentInputL.setVisible(False)
        self.extentInputW.setVisible(False)
        self.getExtent.setVisible(False)
        self.extentInputInterval.setText("0.010000")

    def radio_input_layer(self):
        """Choose between output as memory layer or as shapefile"""
        if self.layerInputMode.isChecked():
            self.labelLayer.setEnabled(True)
            self.layersInput.setEnabled(True)
            self.labelLayer.setVisible(True)
            self.layersInput.setVisible(True)
        else:
            self.labelLayer.setEnabled(False)
            self.layersInput.setEnabled(False)
            self.labelLayer.setVisible(False)
            self.layersInput.setVisible(False)

    def radio_input_extent(self):
        """Choose between output as memory layer or as shapefile"""
        if self.extentInputMode.isChecked():
            self.labelExtent.setEnabled(True)
            self.labelExtentN.setEnabled(True)
            self.labelExtentS.setEnabled(True)
            self.labelExtentL.setEnabled(True)
            self.labelExtentW.setEnabled(True)
            self.labelExtentInterval.setEnabled(True)
            self.extentInputInterval.setEnabled(True)
            self.extentInputN.setEnabled(True)
            self.extentInputS.setEnabled(True)
            self.extentInputL.setEnabled(True)
            self.extentInputW.setEnabled(True)
            self.labelExtent.setVisible(True)
            self.labelExtentN.setVisible(True)
            self.labelExtentS.setVisible(True)
            self.labelExtentL.setVisible(True)
            self.labelExtentW.setVisible(True)
            self.labelExtentInterval.setVisible(True)
            self.extentInputInterval.setVisible(True)
            self.extentInputN.setVisible(True)
            self.extentInputS.setVisible(True)
            self.extentInputL.setVisible(True)
            self.extentInputW.setVisible(True)
            self.getExtent.setVisible(True)
        else:
            self.labelExtent.setEnabled(False)
            self.labelExtentN.setEnabled(False)
            self.labelExtentS.setEnabled(False)
            self.labelExtentL.setEnabled(False)
            self.labelExtentW.setEnabled(False)
            self.labelExtentInterval.setEnabled(False)
            self.extentInputInterval.setEnabled(False)
            self.extentInputN.clear()
            self.extentInputN.setEnabled(False)
            self.extentInputS.clear()
            self.extentInputS.setEnabled(False)
            self.extentInputL.clear()
            self.extentInputL.setEnabled(False)
            self.extentInputW.clear()
            self.extentInputW.setEnabled(False)
            self.labelExtent.setVisible(False)
            self.labelExtentN.setVisible(False)
            self.labelExtentS.setVisible(False)
            self.labelExtentL.setVisible(False)
            self.labelExtentW.setVisible(False)
            self.labelExtentInterval.setVisible(False)
            self.extentInputInterval.setVisible(False)
            self.extentInputN.setVisible(False)
            self.extentInputS.setVisible(False)
            self.extentInputL.setVisible(False)
            self.extentInputW.setVisible(False)
            self.getExtent.setVisible(False)

    def get_extent(self):
        xmin=iface.mapCanvas().extent().xMinimum()
        xmax=iface.mapCanvas().extent().xMaximum()
        ymin=iface.mapCanvas().extent().yMinimum()
        ymax=iface.mapCanvas().extent().yMaximum()
        self.extentInputW.setText(str(xmin))
        self.extentInputL.setText(str(xmax))
        self.extentInputN.setText(str(ymax))
        self.extentInputS.setText(str(ymin))


    ###################
    #OUTPUT
    ###################

    def browseSaveOutput(self):
        """Opens a window to set the location of the output file."""
        fileName0 = QtGui.QFileDialog.getSaveFileName(self, 'Salvar arquivo', self.oldPath, "Shapefile (*.shp);;Todos os arquivos (*)")
        fileName = os.path.splitext(str(fileName0))[0]+'.shp'
        if os.path.splitext(str(fileName0))[0] != '':
            self.oldPath = os.path.dirname(fileName)
        layername = os.path.splitext(os.path.basename(str(fileName)))[0]
        if (layername=='.shp'):
            return
        self.outputFileName.setText(fileName)

    def radio_output(self):
        """Choose between output as memory layer or as shapefile"""
        if self.fileOutput.isChecked():
            self.labelOutputFileName.setEnabled(True)
            self.outputFileName.setEnabled(True)
            self.outputSelectFileName.setEnabled(True)
        else:
            self.labelOutputFileName.setEnabled(False)
            self.outputFileName.clear()
            self.outputFileName.setEnabled(False)
            self.outputSelectFileName.setEnabled(False)

