# LightBlock.py

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSlider, QLabel
from PyQt6.QtCore import pyqtSignal, Qt

class LightBlock(QFrame):
    exposureChanged = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self.topLayout = QVBoxLayout()
        self.setLayout(self.topLayout)

        self.exposureSlider = QSlider(Qt.Orientation.Horizontal)
        self.exposureSlider.setRange(-30, 30)  # Plage de -30 à +30 EV
        self.exposureSlider.setValue(0)  # Valeur par défaut
        self.exposureSlider.valueChanged.connect(self.emitExposureChanged)

        self.exposureValueLabel = QLabel("Exposure: 0.0")
        self.topLayout.addWidget(self.exposureSlider)
        self.topLayout.addWidget(self.exposureValueLabel)

    def emitExposureChanged(self, value):
        ev_value = value / 10.0  # Ajuster l'échelle si nécessaire
        print(f"emitExposureChanged triggered with value: {value}, ev_value: {ev_value}")
        self.exposureValueLabel.setText(f"Exposure: {ev_value:.1f}")
        self.exposureChanged.emit(ev_value)