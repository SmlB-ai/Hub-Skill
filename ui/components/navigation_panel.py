from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal

class NavigationPanel(QWidget):
    productos_clicked = pyqtSignal()
    redes_clicked = pyqtSignal()
    reescalado_clicked = pyqtSignal()
    mockup_clicked = pyqtSignal()
    qr_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        btns = [
            ("📦 Productos", self.productos_clicked),
            ("🌐 Redes Sociales", self.redes_clicked),
            ("🖼️ Reescalado", self.reescalado_clicked),
            ("🧮 MockupGenerator", self.mockup_clicked),
            ("📱 Código QR", self.qr_clicked),
        ]
        for text, signal in btns:
            btn = QPushButton(text)
            btn.clicked.connect(signal)
            layout.addWidget(btn)
        layout.addStretch()