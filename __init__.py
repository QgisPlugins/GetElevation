# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GetElevation
                                 A QGIS plugin
 Plugin Qgis 3.0 para obtenção de dados de elevação da API Google Maps.
                             -------------------
        begin                : 2018-08-31
        copyright            : (C) 2018 by Rodrigo Sousa
        email                : rodrigofrcs@hotmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GetElevation class from file GetElevation.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .get_elevation import GetElevation
    return GetElevation(iface)
