# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GetElevation
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QProgressBar
from qgis.gui import QgsMessageBar
from qgis.core import QgsGeometry, QgsFeatureRequest, QgsSpatialIndex, QgsVectorLayer, QgsFeature, QgsPoint, QgsMapLayerRegistry, QgsVectorFileWriter, QgsProject
# Initialize Qt resources from file resources.py
import resources
# Import libs and the external geographiclib
import timeit, math, sys, os.path; sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/libs")
from geographiclib.geodesic import Geodesic
# Import the code for the dialog
from get_elevation_dialog import GetElevationDialog
import os.path
# Importando bibliotecas necessarias
from xml.etree.ElementTree import ElementTree
import json
import urllib.request
import urllib.parse


class GetElevation:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GetElevation_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Get Elevation')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GetElevation')
        self.toolbar.setObjectName(u'GetElevation')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GetElevation', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = GetElevationDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/GetElevation/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Get Elevation'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Get Elevation'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def showMessage(self, message, level=QgsMessageBar.INFO):
        """Pushes a message to the Message Bar"""
        self.iface.messageBar().pushMessage(message, level, self.iface.messageTimeout())


    def populate(self):
        """Populate the dropdown menu with point vector layers"""
        self.dlg.layersInput.clear()
        for legend in QgsProject.instance().layerTreeRoot().findLayers():
            layer = QgsMapLayerRegistry.instance().mapLayer(legend.layerId())
            if type(layer) == QgsVectorLayer and layer.geometryType() == 0:
                self.dlg.layersInput.addItem(layer.name())


    def get_elevation(self,x,y):
        #CONSTROI A URL PARA A BUSCA DO JSON
        url = 'http://maps.googleapis.com/maps/api/elevation/json?&locations='+str(y)+','+str(x)+'&sensor=false'
        #RECUPERA O JSON
        f = urllib.request.urlopen(url)
        data = f.read().decode('utf-8')
        #PEGA A ELEVACAO
        json_data = json.loads(data)
        elevation = json_data['results'][0]['elevation']
        #RETORNA A ELEVACAO DA COORDENADA PASSADA
        return elevation

    def get_points_by_extent(self, xmin, xmax, ymin, ymax, interval):
        xmin = float(xmin)
        xmax = float(xmax)
        ymin = float(ymin)
        ymax = float(ymax)
        interval = float(interval)
        xextent = xmax-xmin
        yextent = ymax-ymin
        xrangee = int(xextent/interval)
        yrangee = int(yextent/interval)
        points = []
        i=1
        for x in range(0, xrangee):
            xx = (x*interval)+xmin
            for y in range(0, yrangee):
                yy = (y*interval)+ymin
                #print(i)
                #print("x:"+str(xx)+" y:"+str(yy))
                points.append([xx,yy])
                i=i+1
        return(points)

    def run(self):
        """Run method that performs all the real work"""
        #carrega camadas no combobox
        self.populate()
        # exibe a caixa de dialogo
        self.dlg.show()
        # carrega a caixa de dialogo em loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            tic=timeit.default_timer()
            # Obtem todas as camadas validas no projeto
            point_layers = []
            layers = QgsMapLayerRegistry.instance().mapLayers()
            for name, layer in layers.iteritems():
                # Verifica o tipo da camada selecionada (0 for points, 1 for lines, and 2 for polygons)
                if type(layer) == QgsVectorLayer and layer.geometryType() == 0:
                    point_layers.append(layer)
            # Verifica se exite camadas de pontos carregadas
            if self.dlg.layerInputMode.isChecked():
                if len(point_layers) == 0:
                    self.showMessage(self.tr('Nenhuma camada disponivel. Adicione uma camada do tipo pontos ao projeto.'), QgsMessageBar.WARNING)
                    return

                # Obtem o nome da camada selecionada
                layer_name = self.dlg.layersInput.currentText()
                inputLayer = QgsMapLayerRegistry.instance().mapLayersByName(layer_name)[0]
                # Verifica se o SRC eh WGS84 (EPSG:4326)
                if inputLayer.crs().authid() != u'EPSG:4326':
                    self.showMessage(self.tr('A camada selecionada deve estar em coordenadas geograficas (WGS 84, EPSG 4326).'), QgsMessageBar.WARNING)
                    return
            # Verifica se foi definido um caminho para o arquivo de saida
            elif (self.dlg.fileOutput.isChecked() and self.dlg.outputFileName.text() == ''):
                self.showMessage(self.tr('Erro, nao foi definido um arquivo de saida.'),QgsMessageBar.WARNING)
                return

            # Retorna a camada de saida
            if self.dlg.fileOutput.isChecked():
                shapefilename = self.dlg.outputFileName.text()

            # Restringir somente para feicoes selecionadas
            if self.dlg.layerInputMode.isChecked():
                if inputLayer.selectedFeatures():
                    features = inputLayer.selectedFeatures()
                else:
                    features = inputLayer.getFeatures()
                outputName = inputLayer.name()
                crsString = inputLayer.crs().authid()
            else:
                outputName = "Grade_Regular"
                crsString = "EPSG:4326"

            # Criar camada na memoria para os dados de saida
            outputLayer = QgsVectorLayer("Point?crs=" + crsString+"&field=id:integer&field=name:string(20)&field=x:double(20)&field=y:double(20)&field=elev:double(20)&index=yes", "GetElevation_"+outputName, "memory")
            pr = outputLayer.dataProvider()
            outFeat = QgsFeature()



            # Obtem a lista de pontos para processamento
            points = []

            if self.dlg.layerInputMode.isChecked():
                for feature in features:
                    points.append(feature.geometry().asPoint())
            elif self.dlg.extentInputMode.isChecked():
                xmin = self.dlg.extentInputW.text()
                xmax = self.dlg.extentInputL.text()
                ymin = self.dlg.extentInputS.text()
                ymax = self.dlg.extentInputN.text()
                interval = self.dlg.extentInputInterval.text()
                points = self.get_points_by_extent(xmin,xmax,ymin,ymax,interval)



            # Prepara a barra de progresso
            progressMessageBar = self.iface.messageBar()
            progress = QProgressBar()
            progress.setMaximum(100) 
            progressMessageBar.pushWidget(progress)
            lines_total = len(points)-1
            print("Iniciando a consulta da elevacao de um total de "+str(lines_total)+" pontos.")


            print(points)

            # Cria os pontos
            i=1
            for point in points:
                x = point[0]
                y = point[1]
                z = self.get_elevation(x,y)
                print(str(i)+" => "+str(x)+", "+str(y)+", "+str(z))
                # Cria o ponto
                thePoint = QgsPoint(x,y)
                point = QgsGeometry.fromPoint(thePoint)
                outFeat.setGeometry(point)
                # Adiciona os atributos ao ponto
                outFeat.setAttributes([i,'ponto '+str(i),x,y,z])
                pr.addFeatures([outFeat])

                # Set progress
                percent = (i/float(lines_total)) * 100
                progress.setValue(percent)

                i=i+1





            # Redefine a barra de progresso
            self.iface.messageBar().clearWidgets()
            toc=timeit.default_timer()

            # Salva o arquivo na memoria ou em arquivo
            if self.dlg.memoryOutput.isChecked():  # Load memory layer in canvas
                QgsMapLayerRegistry.instance().addMapLayer(outputLayer)
            
            elif self.dlg.fileOutput.isChecked():  # Save shapefile
                QgsVectorFileWriter.writeAsVectorFormat(outputLayer, shapefilename, "utf-8", None, "ESRI Shapefile")

            #exibe amensagem de concluido e fecha a janela
            self.showMessage(self.tr('Concluido!'), QgsMessageBar.SUCCESS)
            self.dlg.close()


            pass
