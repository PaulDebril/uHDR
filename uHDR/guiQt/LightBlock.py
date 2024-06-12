# LightBlock.py

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSlider, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from guiQt.AdvanceSlider import AdvanceSlider
from guiQt.Contrast import Contrast
from guiQt.CurveWidget import CurveWidget
from guiQt.MemoGroup import MemoGroup

class LightBlock(QFrame):
    exposureChanged = pyqtSignal(float)
    contrastChanged = pyqtSignal(float)
    saturationChanged = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)

        # attributes
        self.active : bool = True

        # layout and widgets
        self.topLayout : QVBoxLayout = QVBoxLayout()
        self.setLayout(self.topLayout)

        self.exposure : AdvanceSlider = AdvanceSlider('exposure',0.0,(-30,+30),(-3.0,+3.0),20)
        
        # self.exposureValueLabel = QLabel("Exposure: 0.0")
        self.exposure.valueChanged.connect(self.emitExposureChanged)
        
        self.saturation : AdvanceSlider = AdvanceSlider('saturation',0.0,(-50,+50),(-0.1,+0.1),10000000000)
        # self.exposureValueLabel = QLabel("Exposure: 0.0")
        self.saturation.valueChanged.connect(self.emitSaturationChanged)

        self.contrast : Contrast = Contrast()
        # self.scalingValueLabel = QLabel("Scaling: 0.0")
        self.contrast.scalingChanged.connect(self.emitScalingChanged)

        self.curve : CurveWidget = CurveWidget()
        #self.memory : MemoGroup = MemoGroup()

        ## add to layout
        self.topLayout.addWidget(self.exposure)
        self.topLayout.addWidget(self.saturation)
        # self.topLayout.addWidget(self.exposureValueLabel)
        self.topLayout.addWidget(self.contrast)
        # self.topLayout.addWidget(self.scalingValueLabel)
        self.topLayout.addWidget(self.curve)
        #self.topLayout.addWidget(self.memory)

    def emitExposureChanged(self, value):
        ev_value = value / 10.0  # Ajuster l'échelle si nécessaire
        print(f"emitExposureChanged triggered with value: {value}, ev_value: {ev_value}")
        # self.exposureValueLabel.setText(f"Exposure: {ev_value:.1f}")
        self.exposureChanged.emit(ev_value)

    def emitScalingChanged(self, value):
        print(f"emitScalingChanged triggered with value: {value}")
        # self.scalingValueLabel.setText(f"Scaling: {value:.1f}")
        self.contrastChanged.emit(value)
        
    def emitSaturationChanged(self, value):
        
        print(f"emitSaturationChanged triggered with value: {value}")
        # self.scalingValueLabel.setText(f"Scaling: {value:.1f}")
        self.saturationChanged.emit(value)

