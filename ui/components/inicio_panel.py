import os
import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

PRODUCTOS_FILE = "datos/productos.json"

class InicioPanel(QWidget):
    nuevo_producto_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        # Título
        titulo = QLabel("Bienvenido a Hub-Skill")
        titulo.setStyleSheet("font-size: 24pt; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(titulo)

        # Estadísticas rápidas (inicialmente dummy, luego actualiza con método)
        self.stats_layout = QHBoxLayout()
        
        # Etiquetas para números (se actualizan luego)
        self.lbl_productos = QLabel("0")
        self.lbl_productos.setStyleSheet("font-size: 18pt; color: #4CAF50; font-weight: bold;")
        stats_widget = QWidget()
        stat_layout = QVBoxLayout(stats_widget)
        stat_layout.addWidget(self.lbl_productos)
        stat_layout.addWidget(QLabel("Productos"))
        self.stats_layout.addWidget(stats_widget)

        # Puedes agregar más estadísticas aquí...

        self.layout.addLayout(self.stats_layout)

        # Botón para crear nuevo producto
        btn_nuevo = QPushButton("Crear nuevo producto")
        btn_nuevo.setStyleSheet("font-size: 14pt; padding: 10px 20px; margin-top: 30px;")
        btn_nuevo.clicked.connect(self.nuevo_producto_clicked)
        self.layout.addWidget(btn_nuevo)
        self.layout.addStretch()

        self.actualizar_estadisticas()

    def actualizar_estadisticas(self):
        # Carga el número de productos reales
        if os.path.exists(PRODUCTOS_FILE):
            with open(PRODUCTOS_FILE, "r", encoding="utf-8") as f:
                productos = json.load(f)
            self.lbl_productos.setText(str(len(productos)))
        else:
            self.lbl_productos.setText("0")