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
from math import ceil
from typing_extensions import Self
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLineEdit
from PyQt6.QtWidgets import QHBoxLayout, QWidget, QSplitter, QPushButton, QLabel, QSlider, QCheckBox
from PyQt6.QtCore import pyqtSignal, Qt

from guiQt.FigureWidget import FigureWidget
from guiQt.AdvanceSliderLine import AdvanceSliderLine

from numpy import ndarray
import numpy as np
from geomdl import BSpline, utilities
import copy, time
# ------------------------------------------------------------------------------------------
# --- class CurveWidget(QSplitter) ---------------------------------------------------------
# ------------------------------------------------------------------------------------------

class CurveWidget(QFrame):
    highlightChanged = pyqtSignal(float)
    shadowsChanged = pyqtSignal(float)
    blacksChanged = pyqtSignal(float)
    mediumsChanged = pyqtSignal(float)
    whitesChanged = pyqtSignal(float)
    lightnessMaskChanged = pyqtSignal(dict)  # New signal



    # constructor
    def __init__(self : Self) -> None:
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)

        # attributes
        self.active : bool = True
        ## curve
        self.control = {'start': [0.0, 0.0], 'shadows': [10.0, 10.0], 'blacks': [30.0, 30.0], 'mediums': [50.0, 50.0], 'whites': [70.0, 70.0], 'highlights': [90.0, 90.0], 'end': [100.0, 100.0]}
        self.default = {'start': [0.0, 0.0], 'shadows': [10.0, 10.0], 'blacks': [30.0, 30.0], 'mediums': [50.0, 50.0], 'whites': [70.0, 70.0], 'highlights': [90.0, 90.0], 'end': [100.0, 100.0]}

        self.curve : BSpline.Curve = BSpline.Curve()
        self.curve.degree = 2
        self.points : ndarray|None =None

        ## widgets
        # top laouyt
        self.vbox : QVBoxLayout = QVBoxLayout()

        # figure
        self.curveWidget : FigureWidget = FigureWidget() 
        self.curveWidget.setMinimumSize(200, 200) ### 200,600 ?

        self.curveWidget.plot(np.asarray([0.0,100]),np.asarray([0.0,100.0]),'r--', clear=True)


        # containers
        ## auto
        self.containerAutoActive : QFrame = QFrame() 
        self.hboxAutoActive : QHBoxLayout = QHBoxLayout() 
        self.containerAutoActive.setLayout(self.hboxAutoActive)
        
        # Add checkboxes
        self.checkboxContainer : QFrame = QFrame()
        self.checkboxLayout : QHBoxLayout = QHBoxLayout()
        self.checkboxContainer.setLayout(self.checkboxLayout)

        self.checkbox_shadows = QCheckBox("shadows")
        self.checkbox_blacks = QCheckBox("blacks")
        self.checkbox_mediums = QCheckBox("mediums")
        self.checkbox_whites = QCheckBox("whites")
        self.checkbox_highlights = QCheckBox("highlights")

        # shadows, blacks, mediums, whites, highlights
        self.shadows : AdvanceSliderLine = AdvanceSliderLine('shadows',self.default['shadows'][1],(0,100),(0,100),10) 
        self.blacks : AdvanceSliderLine = AdvanceSliderLine('blacks',self.default['blacks'][1],(0,100),(0,100),10) 
        self.mediums : AdvanceSliderLine = AdvanceSliderLine('mediums',self.default['mediums'][1],(0,100),(0,100),10) 
        self.whites : AdvanceSliderLine = AdvanceSliderLine('whites',self.default['whites'][1],(0,100),(0,100),10) 
        self.highlights = AdvanceSliderLine('highlights', self.default['highlights'][1], (0, 100), (0, 100), 10)

        self.vbox.addWidget(self.curveWidget)
        self.vbox.addWidget(self.containerAutoActive) #  zj add for semi-auto curve 
        
        self.vbox.addWidget(self.checkboxContainer)
        self.checkboxLayout.addWidget(self.checkbox_shadows)
        self.checkboxLayout.addWidget(self.checkbox_blacks)
        self.checkboxLayout.addWidget(self.checkbox_mediums)
        self.checkboxLayout.addWidget(self.checkbox_whites)
        self.checkboxLayout.addWidget(self.checkbox_highlights)
        
        self.checkbox_shadows.stateChanged.connect(self.emitsLightnessMask)
        self.checkbox_blacks.stateChanged.connect(self.emitsLightnessMask)
        self.checkbox_mediums.stateChanged.connect(self.emitsLightnessMask)
        self.checkbox_whites.stateChanged.connect(self.emitsLightnessMask)
        self.checkbox_highlights.stateChanged.connect(self.emitsLightnessMask)


        self.vbox.addWidget(self.highlights)
        self.vbox.addWidget(self.whites)
        self.vbox.addWidget(self.mediums)
        self.vbox.addWidget(self.blacks)
        self.vbox.addWidget(self.shadows)

        # autoCurve button
        self.autoCurve = QPushButton("auto")

        # active checkbox
        self.checkBoxActive : QCheckBox = QCheckBox("active")
        self.checkBoxActive.setChecked(True)

        # layout Auto and Active
        self.hboxAutoActive.addStretch()
        self.hboxAutoActive.addWidget(self.autoCurve)
        self.hboxAutoActive.addStretch()
        self.hboxAutoActive.addWidget(self.checkBoxActive)

        # layout
        self.setLayout(self.vbox)

        # callBackFunctions slider/reset
        self.shadows.valueChanged.connect(self.CBsliderChanged)
        self.blacks.valueChanged.connect(self.CBsliderChanged)
        self.mediums.valueChanged.connect(self.CBsliderChanged)
        self.whites.valueChanged.connect(self.CBsliderChanged)
        self.highlights.valueChanged.connect(self.CBsliderChanged)
        self.shadows.valueChanged.connect(self.CBsliderChanged)
        self.blacks.valueChanged.connect(self.CBsliderChanged)

        # self.highlights.valueChanged.connect(self.emitHighlightChanged)

        #self.autoCurve.clicked.connect(self.controller.autoCurve)  #  zj add for semi-auto curve 

        # updateKeys
        self.updateKeys()
        # evaluate
        self.evaluate()
        # clear plot
        self.curveWidget.plot(np.asarray([0.0,100]),np.asarray([0.0,100.0]),'r--', clear=True)
        #plotCurve
        self.plotCurve()
                                                                                         
    # methods
    ## callbacks
    def CBsliderChanged(self : Self, key : str, val :float) -> None:
        
        print(f"Slider value changed: {key} = {val}")
        if self.active:
            self.setKey(key, val, False)
            if key == 'highlights':
                self.emitHighlightChanged(val)
            elif key == 'shadows':
                self.emitShadowsChanged(val)
            elif key == 'blacks':
                self.emitBlacksChanged(val)
            elif key == 'mediums':
                self.emitMediumsChanged(val)
            elif key == 'whites':
                self.emitWhitesChanged(val)
        # print('vaalllll', val)
        # if self.active: 
        #     self.setKey(key, val, False)

            

    def emitHighlightChanged(self, value: float) -> None:
        print(f"emitHighlightChanged in CurveWidget: {value}")
        self.highlightChanged.emit(value)
        
    def emitShadowsChanged(self, value: float) -> None:
        print(f"emitShadowsChanged in CurveWidget: {value}")
        self.shadowsChanged.emit(value)
        
    def emitBlacksChanged(self, value: float) -> None:
        print(f"emitBlacksChanged in CurveWidget: {value}")
        self.blacksChanged.emit(value)
        
    def emitMediumsChanged(self, value: float) -> None:
        print(f"emitMediumsChanged in CurveWidget: {value}")
        self.mediumsChanged.emit(value)
        
    def emitWhitesChanged(self, value: float) -> None:
        print(f"emitWhitesChanged in CurveWidget: {value}")
        self.whitesChanged.emit(value)
        
    def emitsLightnessMask(self):
        mask = {
        'shadows': self.checkbox_shadows.isChecked(),
        'blacks': self.checkbox_blacks.isChecked(),
        'mediums': self.checkbox_mediums.isChecked(),
        'whites': self.checkbox_whites.isChecked(),
        'highlights': self.checkbox_highlights.isChecked()
        }
        print("CurveWidget EMIT:",mask)
        self.lightnessMaskChanged.emit(mask)

        
    ## updateKeys
    def updateKeys(self : Self) -> None:
        self.active = False
        self.shadows.setValue(self.control['shadows'][1])
        self.blacks.setValue(self.control['blacks'][1])
        self.mediums.setValue(self.control['mediums'][1])
        self.whites.setValue(self.control['whites'][1])
        self.highlights.setValue(self.control['highlights'][1])
        self.active = True

    ## setValue
    def setKey(self : Self, key : str , value : int|float, autoScale :bool =False) -> None:
        value = float(value)

        # check key
        if key in self.control.keys():
            # transform in list
            listKeys = list(self.control.keys())
            listValues = np.asarray(list(self.control.values()))
            index = listKeys.index(key)

            if (listValues[:index,1] <= value).all() and (value <= listValues[index+1:,1]).all():
                # can change
                oldValue = self.control[listKeys[index]]
                self.control[listKeys[index]] = [oldValue[0],value] 

            elif not (value <= listValues[index+1:,1]).all():
                if autoScale:
                    minValue = min(listValues[index:,1])
                    maxValue = listValues[-1:,1]
                    u = (listValues[index+1:,1] -minValue)/(maxValue-minValue)

                    newValues = value*(1- u)+ u*maxValue
                    for i,v in enumerate(newValues):
                        oldValue = self.control[listKeys[i+index+1]]
                        self.control[listKeys[i+index+1]] = [oldValue[0],np.round(v)]
                else:
                    # not autoScale, set to minValue
                    oldValue = self.control[listKeys[index]]
                    minValue = min(listValues[index+1:,1])
                    self.control[listKeys[index]] = [oldValue[0],minValue]

            elif not (listValues[:index,1] <= value).all():
                if autoScale:
                    minValue = listValues[0,1]
                    maxValue = max(listValues[:index,1])
                    u = (listValues[:index,1] -minValue)/(maxValue-minValue)
                    newValues = minValue*(1- u)+ u*value
                    for i,v in enumerate(newValues):
                        oldValue = self.control[listKeys[i]]
                        self.control[listKeys[i]] = [oldValue[0],np.round(v)]
                else:
                    # not autoScale, set to maxValue
                    oldValue = self.control[listKeys[index]]
                    maxValue =  max(listValues[:index,1])
                    self.control[listKeys[index]] = [oldValue[0],maxValue]

        # updateKeys
        self.updateKeys()
        # evaluate
        self.evaluate()
        # clear plot
        self.curveWidget.plot(np.asarray([0.0,100]),np.asarray([0.0,100.0]),'r--', clear=True)
        #plotCurve
        self.plotCurve()

    ## evalutae curve
    def evaluate(self : Self) -> None:
        self.curve.ctrlpts = copy.deepcopy([self.control['start'],self.control['shadows'],self.control['blacks'],self.control['mediums'], self.control['whites'], self.control['highlights'], [200, self.control['end'][1]]])
        # auto-generate knot vector
        self.curve.knotvector = utilities.generate_knot_vector(self.curve.degree, len(self.curve.ctrlpts))
        # evaluate curve and get points
        self.points = np.asarray(self.curve.evalpts)

    ## plotCurve
    def plotCurve(self):
        try:
            self.curveWidget.plot(np.asarray([0,100]),np.asarray([0,100]),'r--', clear=True)
            self.curveWidget.plot(np.asarray([20,20]),np.asarray([0,100]),'r--', clear=False)
            self.curveWidget.plot(np.asarray([40,40]),np.asarray([0,100]),'r--', clear=False)
            self.curveWidget.plot(np.asarray([60,60]),np.asarray([0,100]),'r--', clear=False)
            self.curveWidget.plot(np.asarray([80,80]),np.asarray([0,100]),'r--', clear=False)

            controlPointCoordinates= np.asarray(self.curve.ctrlpts)
            self.curveWidget.plot(controlPointCoordinates[1:-1,0],controlPointCoordinates[1:-1,1],'ro', clear=False)
            if isinstance(self.points, ndarray):
                x = self.points[:,0]
                self.curveWidget.plot(self.points[x<100,0],self.points[x<100,1],'r',clear=False)
        except:
            print(f'CurveWidget.plotCurve():[error in plotting curve]')
            time.sleep(0.5)
            self.plotCurve()

# -------------------------------------------------------------------------------------------
