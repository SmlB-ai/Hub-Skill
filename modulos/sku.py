import os
import json
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QHBoxLayout, QPushButton,
    QMessageBox, QLineEdit, QApplication
)
from PyQt6.QtCore import Qt

DATA_DIR = "datos"
PRODUCTOS_FILE = os.path.join(DATA_DIR, "productos.json")
MARCAS_FILE = os.path.join(DATA_DIR, "marcas.json")
NOMBRES_PRODUCTO_FILE = os.path.join(DATA_DIR, "nombres_producto.json")
TECNICAS_FILE = os.path.join(DATA_DIR, "tecnicas.json")
TAMANOS_FILE = os.path.join(DATA_DIR, "tamanos.json")
COLORES_FILE = os.path.join(DATA_DIR, "colores.json")
FORMAS_FILE = os.path.join(DATA_DIR, "formas.json")

class SkuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de SKUs")
        self.setMinimumSize(950, 650)

        # Cargar catálogos y productos
        self.productos = []
        self.marcas = []
        self.nombres_producto = []
        self.tecnicas = []
        self.tamanos = []
        self.colores = []
        self.formas = []

        self.filtered_indices = []  # Para mapear lista filtrada al índice real

        self.load_catalogs_and_products()
        self.init_ui()

    def load_json(self, file, default):
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        return default

    def load_catalogs_and_products(self):
        self.productos = self.load_json(PRODUCTOS_FILE, [])
        self.marcas = self.load_json(MARCAS_FILE, ["Sin marca"])
        self.nombres_producto = self.load_json(NOMBRES_PRODUCTO_FILE, ["Playera", "Taza", "Poster", "Sudadera"])
        self.tecnicas = self.load_json(TECNICAS_FILE, ["Sublimación", "DTF", "Vinil"])
        self.tamanos = self.load_json(TAMANOS_FILE, ["Chico", "Mediano", "Grande"])
        self.colores = self.load_json(COLORES_FILE, ["Blanco", "Negro", "Rojo"])
        self.formas = self.load_json(FORMAS_FILE, ["Redondo", "Rectangular", "Cuadrado"])

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        title_label = QLabel("Gestión de SKUs")
        title_label.setStyleSheet("font-size: 22pt; font-weight: bold; margin-bottom: 15px;")
        main_layout.addWidget(title_label)

        # Barra de búsqueda
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por SKU, nombre, marca, diseño, etc.")
        self.search_input.textChanged.connect(self.refresh_product_list)
        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.clicked.connect(lambda: self.search_input.setText(""))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_limpiar)
        main_layout.addLayout(search_layout)

        # Lista de productos con SKUs
        self.lista_productos = QListWidget()
        self.refresh_product_list()
        self.lista_productos.setMinimumHeight(350)
        main_layout.addWidget(self.lista_productos)

        # Campo SKU y botón copiar
        h_sku = QHBoxLayout()
        self.sku_input = QLineEdit()
        self.sku_input.setReadOnly(True)
        self.sku_input.setPlaceholderText("Selecciona un producto para ver su SKU")
        btn_copiar = QPushButton("Copiar SKU")
        h_sku.addWidget(self.sku_input)
        h_sku.addWidget(btn_copiar)
        main_layout.addLayout(h_sku)

        # Botón para refrescar manualmente
        btn_refrescar = QPushButton("Refrescar lista")
        btn_refrescar.clicked.connect(self.reload_and_refresh)
        main_layout.addWidget(btn_refrescar)

        # Señales
        self.lista_productos.currentRowChanged.connect(self.mostrar_sku_actual)
        btn_copiar.clicked.connect(self.copiar_sku_al_portapapeles)

        # Botón para actualizar todos los SKUs en el JSON
        btn_actualizar = QPushButton("Actualizar todos los SKUs en productos.json")
        btn_actualizar.clicked.connect(self.actualizar_todos_los_skus)
        main_layout.addWidget(btn_actualizar)

    def catalog_index_code(self, value, catalog, letter):
        try:
            idx = catalog.index(value)
        except ValueError:
            idx = 0
        return f"{idx+1:02d}{letter}"

    def producto_index_code(self, value):
        try:
            idx = self.nombres_producto.index(value)
        except ValueError:
            idx = 0
        return f"{idx+1:02d}P"

    def tecnica_index_code(self, value):
        try:
            idx = self.tecnicas.index(value)
        except ValueError:
            idx = 0
        return f"{idx+1:02d}T"

    def color_index_code(self, value):
        try:
            idx = self.colores.index(value)
        except ValueError:
            idx = 0
        return f"{idx+1:02d}C"

    def tamano_index_code(self, value):
        try:
            idx = self.tamanos.index(value)
        except ValueError:
            idx = 0
        return f"{idx+1:02d}S"

    def forma_index_code(self, value):
        try:
            idx = self.formas.index(value)
        except ValueError:
            idx = 0
        return f"{idx+1:02d}F"

    def diseño_code(self, value):
        if not value:
            return "DSN"
        d = value.replace(" ", "").upper()
        # Quita acentos básicos
        d = re.sub(r'[ÁÀÂÄ]', 'A', d)
        d = re.sub(r'[ÉÈÊË]', 'E', d)
        d = re.sub(r'[ÍÌÎÏ]', 'I', d)
        d = re.sub(r'[ÓÒÔÖ]', 'O', d)
        d = re.sub(r'[ÚÙÛÜ]', 'U', d)
        d = re.sub(r'[^A-Z0-9]', '', d)  # Solo letras y números
        return d[:3]

    def calcular_sku(self, producto):
        cod_marca = self.catalog_index_code(producto.get("marca", ""), self.marcas, "M")
        cod_producto = self.producto_index_code(producto.get("nombre", ""))
        cod_tecnica = self.tecnica_index_code(producto.get("tecnica", ""))
        cod_color = self.color_index_code(producto.get("color", ""))
        cod_tamano = self.tamano_index_code(producto.get("tamano", ""))
        cod_forma = self.forma_index_code(producto.get("forma", ""))
        cod_diseno = self.diseño_code(producto.get("diseno", ""))
        return f"{cod_marca}-{cod_producto}-{cod_tecnica}-{cod_color}-{cod_tamano}-{cod_forma}-{cod_diseno}"

    def refresh_product_list(self):
        filtro = self.search_input.text().strip().upper()
        self.lista_productos.clear()
        self.filtered_indices = []
        for idx, p in enumerate(self.productos):
            sku = self.calcular_sku(p)
            campos = [
                sku,
                p.get("nombre", ""),
                p.get("marca", ""),
                p.get("tecnica", ""),
                p.get("tamano", ""),
                p.get("color", ""),
                p.get("forma", ""),
                p.get("diseno", ""),
                p.get("categoria", ""),
                p.get("subcategoria", "")
            ]
            texto_busqueda = " ".join([str(c).upper() for c in campos])
            if filtro == "" or filtro in texto_busqueda:
                txt = f'{sku} | {p.get("nombre","")} ({p.get("marca","")}) [{p.get("diseno","")}]'
                self.lista_productos.addItem(txt)
                self.filtered_indices.append(idx)

    def mostrar_sku_actual(self, idx):
        if idx < 0 or idx >= len(self.filtered_indices):
            self.sku_input.clear()
            return
        real_idx = self.filtered_indices[idx]
        p = self.productos[real_idx]
        sku = self.calcular_sku(p)
        self.sku_input.setText(sku)

    def copiar_sku_al_portapapeles(self):
        sku = self.sku_input.text()
        if not sku:
            return
        QApplication.clipboard().setText(sku)
        QMessageBox.information(self, "Copiado", f"SKU '{sku}' copiado al portapapeles.")

    def reload_and_refresh(self):
        self.load_catalogs_and_products()
        self.refresh_product_list()
        self.sku_input.clear()

    def actualizar_todos_los_skus(self):
        if not self.productos:
            QMessageBox.warning(self, "Error", "No hay productos cargados.")
            return

        # Actualiza todos los SKUs en el JSON
        for prod in self.productos:
            prod["sku"] = self.calcular_sku(prod)

        with open(PRODUCTOS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.productos, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "Listo", "Todos los SKUs fueron actualizados en productos.json.\nAhora puedes usar el módulo de reescalado sin problemas.")
        self.reload_and_refresh()