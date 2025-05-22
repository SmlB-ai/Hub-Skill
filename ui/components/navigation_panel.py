from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal

class NavigationPanel(QWidget):
    inicio_clicked = pyqtSignal()
    productos_clicked = pyqtSignal()
    sku_clicked = pyqtSignal()
    imagenes_clicked = pyqtSignal()
    urls_clicked = pyqtSignal()
    publicar_clicked = pyqtSignal()
    medidas_clicked = pyqtSignal()
    precios_clicked = pyqtSignal()
    descripcion_clicked = pyqtSignal()  # <--- NEW: Señal para Descripción/Contenido

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        btns = [
            ("🏠 Inicio", self.inicio_clicked),
            ("📦 Datos de producto", self.productos_clicked),
            ("🔖 SKU y Códigos", self.sku_clicked),
            ("🖼️ Imágenes", self.imagenes_clicked),
            ("🔗 URLs", self.urls_clicked),
            ("📏 Medidas de productos", self.medidas_clicked),
            ("💲 Precios y Dinero", self.precios_clicked),
            ("📝 Descripción/Contenido", self.descripcion_clicked),  # <--- NUEVO BOTÓN
            ("🔳 Generador QR", self.publicar_clicked),
        ]
        for text, signal in btns:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 14pt;
                    padding: 10px;
                    text-align: left;
                    border: none;
                    background: transparent;
                }
                QPushButton:hover {
                    background-color: rgba(76, 175, 80, 0.1);
                }
            """)
            btn.clicked.connect(signal)
            layout.addWidget(btn)
        layout.addStretch()