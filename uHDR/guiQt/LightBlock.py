# LightBlock.py

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSlider, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from guiQt.AdvanceSlider import AdvanceSlider
from guiQt.Contrast import Contrast
from guiQt.CurveWidget import CurveWidget
from guiQt.MemoGroup import MemoGroup

class LightBlock(QFrame):
    exposureChanged = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)

        # attributes
        self.active : bool = True

        # layout and widgets
        self.topLayout : QVBoxLayout = QVBoxLayout()
        self.setLayout(self.topLayout)


        self.exposure : AdvanceSlider =AdvanceSlider('exposure',0.0,(-30,+30),(-3.0,+3.0),10)
        self.exposureValueLabel = QLabel("Exposure: 0.0")
        self.exposure.valueChanged.connect(self.emitExposureChanged)
        self.contrast :  Contrast =Contrast()
        self.curve :  CurveWidget =CurveWidget()
        #self.memory : MemoGroup = MemoGroup()

        ## add to layout
        self.topLayout.addWidget(self.exposure)
        self.topLayout.addWidget(self.contrast)
        self.topLayout.addWidget(self.curve)
        #self.topLayout.addWidget(self.memory)

    def emitExposureChanged(self, value):
        ev_value = value / 10.0  # Ajuster l'échelle si nécessaire
        print(f"emitExposureChanged triggered with value: {value}, ev_value: {ev_value}")
        self.exposureValueLabel.setText(f"Exposure: {ev_value:.1f}")
        self.exposureChanged.emit(ev_value)