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
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QTabWidget
from PyQt6.QtGui import QDoubleValidator, QIntValidator 
from PyQt6.QtCore import Qt, pyqtSignal, QLocale

from guiQt.LightBlockScroll import LightBlockScroll
from guiQt.ColorBlockScroll import ColorBlockScroll

# ------------------------------------------------------------------------------------------
# --- class Editor (QTabWidget) ------------------------------------------------------
# ------------------------------------------------------------------------------------------
class Editor(QTabWidget):
    exposureChanged = pyqtSignal(float)  
    saturationChanged = pyqtSignal(float)  
    contrastChanged = pyqtSignal(float)
    highlightChanged = pyqtSignal(float)  # Signal pour les "highlights"
    shadowsChanged = pyqtSignal(float)
    blacksChanged = pyqtSignal(float)
    mediumsChanged = pyqtSignal(float)
    whitesChanged = pyqtSignal(float)
    selectionChanged = pyqtSignal(dict)  # Signal pour les changements de sélection
    editorValueChanged = pyqtSignal(dict)
    showSelectionChanged = pyqtSignal(bool) # Signal pour afficher la mask ou non
    lightnessMaskChanged = pyqtSignal(dict)

    


    # class attributes
    ## signal

    # constructor
    def __init__(self:Self) -> None:
        super().__init__()

        # attributes
        self.lightEdit : LightBlockScroll = LightBlockScroll() 

        
        self.nbColorEditor : int = 5       
        self.colorEdits : list[ColorBlockScroll] = []
        for i in range(self.nbColorEditor): 
            colorEdit = ColorBlockScroll()
            colorEdit.selectionChanged.connect(self.onSelectionChanged)
            colorEdit.editorValueChanged.connect(self.editorValueChanged.emit)
            colorEdit.showSelectionChanged.connect(self.onShowSelectionChanged)
            self.colorEdits.append(colorEdit)

        # QTabWidget settup
        self.setTabPosition(QTabWidget.TabPosition.East)
        self.setMovable(True)

        # add widgets
        self.addTab(self.lightEdit,"Light")
        for i in range(self.nbColorEditor): self.addTab(self.colorEdits[i],"Color "+str(i))

        self.lightEdit.exposureChanged.connect(self.exposureChanged)
        self.lightEdit.saturationChanged.connect(self.saturationChanged)
        self.lightEdit.contrastChanged.connect(self.contrastChanged)
        self.lightEdit.highlightChanged.connect(self.onHighlightChanged)
        self.lightEdit.shadowsChanged.connect(self.onShadowsChanged)
        self.lightEdit.blacksChanged.connect(self.onBlacksChanged)
        self.lightEdit.mediumsChanged.connect(self.onMediumsChanged)
        self.lightEdit.whitesChanged.connect(self.onWhitesChanged)
        self.lightEdit.lightnessMaskChanged.connect(self.onLightnessMaskChanged)



    def onHighlightChanged(self, value: float) -> None:
        print(f"in Editor: {value}")
        self.highlightChanged.emit(value)
        
    def onShadowsChanged(self, value: float) -> None:
        print(f"in Editor: {value}")
        self.shadowsChanged.emit(value)
        
    def onBlacksChanged(self, value: float) -> None:
        print(f"in Editor: {value}")
        self.blacksChanged.emit(value)
        
    def onMediumsChanged(self, value: float) -> None:
        print(f"in Editor: {value}")
        self.mediumsChanged.emit(value)
        
    def onWhitesChanged(self, value: float) -> None:
        print(f"in Editor: {value}")
        self.whitesChanged.emit(value)
        
    def onSelectionChanged(self, selection: dict) -> None:
        self.selectionChanged.emit(selection)
        
    def onShowSelectionChanged(self, show: bool) -> None:
        print("Editor.py : Afficher la mask ? : ", show)
        self.showSelectionChanged.emit(show)
        
    def onLightnessMaskChanged(self, mask: dict) -> None:
        print(f"in Editor: {mask}")
        self.lightnessMaskChanged.emit(mask)
