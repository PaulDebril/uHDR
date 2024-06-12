# uHDR: HDR image editing software
#   Copyright (C) 2022  remi cozot 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
# hdrCore project 2020-2022
# author: remi.cozot@univ-littoral.fr

# import
# ------------------------------------------------------------------------------------------
from typing_extensions import Self
from PyQt6.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QPushButton, QMainWindow
from PyQt6.QtGui import QDoubleValidator, QIntValidator 
from PyQt6.QtCore import Qt, pyqtSignal, QLocale, QSize

from guiQt.LightBlock import LightBlock


# ------------------------------------------------------------------------------------------
# --- class LightBlockScroll (QScrollArea) -------------------------------------------------
# ------------------------------------------------------------------------------------------
class LightBlockScroll(QScrollArea):
    exposureChanged = pyqtSignal(float)  # Signal pour transmettre l'exposition
    contrastChanged = pyqtSignal(float)  # Signal pour transmettre l'exposition
    saturationChanged = pyqtSignal(float)
    highlightChanged = pyqtSignal(float)  # Signal pour les "highlights"
    shadowsChanged = pyqtSignal(float)
    blacksChanged = pyqtSignal(float)

    # class attributes
    ## signal

    # constructor
    def __init__(self : Self) -> None:
        super().__init__()


        ## lightblock widget
        self.light : LightBlock = LightBlock()
        self.light.setMinimumSize(500,1500)


        ## Scroll Area Properties
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True) 

        self.setWidget(self.light)
        
        self.light.exposureChanged.connect(self.exposureChanged)
        self.light.saturationChanged.connect(self.saturationChanged)
        self.light.contrastChanged.connect(self.contrastChanged)
        self.light.highlightChanged.connect(self.onHighlightChanged)
        self.light.shadowsChanged.connect(self.onShadowsChanged)
        self.light.blacksChanged.connect(self.onBlacksChanged)


    def onHighlightChanged(self, value: float) -> None:
        print(f"in LightBlockScroll: {value}")
        self.highlightChanged.emit(value)
        
    def onShadowsChanged(self, value: float) -> None:
        print(f"in LightBlockScroll: {value}")
        self.shadowsChanged.emit(value)
        
    def onBlacksChanged(self, value: float) -> None:
        print(f"in LightBlockScroll: {value}")
        self.blacksChanged.emit(value)
# ------------------------------------------------------------------------------------------


