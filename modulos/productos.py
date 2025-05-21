from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QHBoxLayout)
from PyQt6.QtCore import Qt

class ProductosWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Productos")
        self.setMinimumSize(800, 600)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Título
        title_label = QLabel("Productos")
        title_label.setStyleSheet("font-size: 24pt; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Lista de productos (simulada por ahora)
        self.lista_productos = QListWidget()
        self.lista_productos.addItems([
            "Playera - Jaguar Blanco - SKU001",
            "Taza - Diseño Calavera - SKU002",
            "Poster - México Mágico - SKU003",
            "Sudadera - Guerrero Águila - SKU004",
        ])
        main_layout.addWidget(self.lista_productos)

        # Botones de acciones
        button_layout = QHBoxLayout()
        btn_agregar = QPushButton("Agregar Producto")
        btn_editar = QPushButton("Editar Seleccionado")
        btn_exportar = QPushButton("Exportar a CSV")

        button_layout.addWidget(btn_agregar)
        button_layout.addWidget(btn_editar)
        button_layout.addWidget(btn_exportar)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
