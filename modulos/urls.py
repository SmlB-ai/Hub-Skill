import os
import json
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QGuiApplication

DATA_DIR = "datos"
PRODUCTOS_FILE = os.path.join(DATA_DIR, "productos.json")
DEFAULT_IMAGES_ROOT = os.path.abspath("imagenes_productos")
DEFAULT_URL_BASE = "http://skillhub-mex.com/wp-content/uploads/"

class UrlsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de URLs de Imágenes")
        self.setMinimumSize(700, 400)
        self.imagenes_raiz = DEFAULT_IMAGES_ROOT
        self.productos = []
        self.sku_seleccionado = ""
        self.carpeta_actual = ""
        self.init_ui()
        self.cargar_productos()
        self.actualizar_urls()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Campo URL base
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL base:"))
        self.url_base_edit = QLineEdit(DEFAULT_URL_BASE)
        url_layout.addWidget(self.url_base_edit)
        layout.addLayout(url_layout)

        # Selector de producto
        prod_layout = QHBoxLayout()
        prod_layout.addWidget(QLabel("Producto:"))
        self.producto_combo = QComboBox()
        self.producto_combo.currentIndexChanged.connect(self.cambiar_producto)
        prod_layout.addWidget(self.producto_combo)
        layout.addLayout(prod_layout)

        # Área de URLs generadas
        self.urls_edit = QTextEdit()
        self.urls_edit.setReadOnly(True)
        layout.addWidget(self.urls_edit)

        # Botón copiar
        btn_layout = QHBoxLayout()
        self.btn_copiar = QPushButton("Copiar URLs al portapapeles")
        self.btn_copiar.clicked.connect(self.copiar_urls)
        btn_layout.addWidget(self.btn_copiar)
        layout.addLayout(btn_layout)

    def cargar_productos(self):
        self.productos = []
        if os.path.exists(PRODUCTOS_FILE):
            with open(PRODUCTOS_FILE, "r", encoding="utf-8") as f:
                self.productos = json.load(f)
        self.producto_combo.clear()
        for prod in self.productos:
            sku = prod.get("sku", "")
            nombre = prod.get("nombre", "")
            marca = prod.get("marca", "")
            diseno = prod.get("diseno", "")
            texto = f"{sku} | {nombre} ({marca})"
            if diseno:
                texto += f" [{diseno}]"
            self.producto_combo.addItem(texto, userData=sku)
        if self.productos:
            self.sku_seleccionado = self.productos[0].get("sku", "")
            self.carpeta_actual = os.path.join(self.imagenes_raiz, self.sku_seleccionado)

    def cambiar_producto(self, idx):
        if idx < 0 or idx >= len(self.productos):
            return
        self.sku_seleccionado = self.productos[idx].get("sku", "")
        self.carpeta_actual = os.path.join(self.imagenes_raiz, self.sku_seleccionado)
        self.actualizar_urls()

    def actualizar_urls(self):
        if not self.sku_seleccionado or not os.path.exists(self.carpeta_actual):
            self.urls_edit.setPlainText("")
            return
        # Año/mes actual
        now = datetime.datetime.now()
        anio = now.strftime("%Y")
        mes = now.strftime("%m")
        base = self.url_base_edit.text().rstrip("/") + f"/{anio}/{mes}/"

        urls = []
        for f in os.listdir(self.carpeta_actual):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif')):
                urls.append(base + f)
        self.urls_edit.setPlainText("\n".join(urls))

    def copiar_urls(self):
        texto = self.urls_edit.toPlainText()
        if texto:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(texto)
            QMessageBox.information(self, "Copiado", "¡URLs copiadas al portapapeles!")

    # Si quieres que se actualicen al cambiar la URL base:
    def showEvent(self, event):
        self.url_base_edit.textChanged.connect(self.actualizar_urls)
        super().showEvent(event)