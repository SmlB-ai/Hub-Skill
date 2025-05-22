import os
import json
import uuid
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QComboBox, QListWidget, QFormLayout, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt

PRODUCTOS_FILE = "datos/productos.json"

def cargar_productos():
    if os.path.exists(PRODUCTOS_FILE):
        with open(PRODUCTOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_productos(productos):
    with open(PRODUCTOS_FILE, "w", encoding="utf-8") as f:
        json.dump(productos, f, ensure_ascii=False, indent=2)

class ProductosWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Productos")
        self.productos = cargar_productos()
        self.categorias = self.cargar_categorias()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        form = QFormLayout()

        self.sku_input = QLineEdit()
        form.addRow("SKU:", self.sku_input)
        self.nombre_combo = QComboBox()
        self.nombre_combo.addItems(self.cargar_nombres_producto())
        form.addRow("Nombre:", self.nombre_combo)
        self.marca_combo = QComboBox()
        self.marca_combo.addItems(self.cargar_marcas())
        form.addRow("Marca:", self.marca_combo)
        self.tecnica_combo = QComboBox()
        self.tecnica_combo.addItems(self.cargar_tecnicas())
        form.addRow("Técnica:", self.tecnica_combo)
        self.tamano_combo = QComboBox()
        self.tamano_combo.addItems(self.cargar_tamanos())
        form.addRow("Tamaño:", self.tamano_combo)
        self.color_combo = QComboBox()
        self.color_combo.addItems(self.cargar_colores())
        form.addRow("Color:", self.color_combo)
        self.forma_combo = QComboBox()
        self.forma_combo.addItems(self.cargar_formas())
        form.addRow("Forma:", self.forma_combo)
        self.diseno_input = QLineEdit()
        form.addRow("Diseño:", self.diseno_input)
        self.categoria_combo = QComboBox()
        self.categoria_combo.addItems(list(self.categorias.keys()))
        self.categoria_combo.currentIndexChanged.connect(self.update_subcategorias)
        form.addRow("Categoría:", self.categoria_combo)
        self.subcategoria_combo = QComboBox()
        if self.categorias:
            self.update_subcategorias()
        form.addRow("Subcategoría:", self.subcategoria_combo)

        main_layout.addLayout(form)

        # Lista de productos
        self.lista_productos = QListWidget()
        self.refresh_product_list()
        main_layout.addWidget(self.lista_productos)

        # Botones básicos
        button_layout = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar Producto")
        self.btn_agregar.clicked.connect(self.agregar_producto)
        self.btn_editar = QPushButton("Editar Seleccionado")
        self.btn_editar.clicked.connect(self.editar_producto)
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_producto)
        button_layout.addWidget(self.btn_agregar)
        button_layout.addWidget(self.btn_editar)
        button_layout.addWidget(self.btn_eliminar)
        main_layout.addLayout(button_layout)

        self.lista_productos.currentRowChanged.connect(self.cargar_producto_en_formulario)

    # Métodos para cargar catálogos auxiliares (puedes modificar para cargar desde archivo si lo deseas)
    def cargar_nombres_producto(self):
        path = "datos/nombres_producto.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return ["Playera", "Taza", "Poster", "Sudadera", "Tote Bag"]

    def cargar_marcas(self):
        return ["SkillHub", "Woof Arhini", "Sin marca"]

    def cargar_tecnicas(self):
        return ["Sublimación", "DTF", "Ninguna (materia Prima)"]

    def cargar_tamanos(self):
        return ["S", "M", "L", "XL", "11 oz", "35x40 Tote", "Chico"]

    def cargar_colores(self):
        return ["Blanco", "Negro", "Crudo"]

    def cargar_formas(self):
        return ["Rectangular", "Normal"]

    def cargar_categorias(self):
        path = "datos/categorias.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        # fallback por si no existe el archivo
        return {
            "Tazas": ["Taza Blanca", "Taza Negra", "Termos"],
            "Ropa": ["Playeras", "Sudaderas"],
            "Bolsas Tote": [""]
        }

    def update_subcategorias(self):
        cat = self.categoria_combo.currentText()
        self.subcategoria_combo.clear()
        self.subcategoria_combo.addItems(self.categorias.get(cat, [""]))

    def get_form_data(self):
        idx = self.lista_productos.currentRow()
        prod_id = None
        if idx >= 0 and idx < len(self.productos):
            prod_id = self.productos[idx].get("id")
        if not prod_id:
            prod_id = str(uuid.uuid4())
        return {
            "id": prod_id,
            "sku": self.sku_input.text().strip(),
            "nombre": self.nombre_combo.currentText(),
            "marca": self.marca_combo.currentText(),
            "tecnica": self.tecnica_combo.currentText(),
            "tamano": self.tamano_combo.currentText(),
            "color": self.color_combo.currentText(),
            "forma": self.forma_combo.currentText(),
            "diseno": self.diseno_input.text().strip(),
            "categoria": self.categoria_combo.currentText(),
            "subcategoria": self.subcategoria_combo.currentText()
        }

    def agregar_producto(self):
        data = self.get_form_data()
        if not data["nombre"]:
            QMessageBox.warning(self, "Campos requeridos", "El nombre del producto es obligatorio.")
            return
        self.productos.append(data)
        guardar_productos(self.productos)
        self.refresh_product_list()
        self.clear_form()

    def editar_producto(self):
        idx = self.lista_productos.currentRow()
        if idx < 0:
            QMessageBox.information(self, "Selecciona", "Elige un producto para editar.")
            return
        data = self.get_form_data()
        if not data["nombre"]:
            QMessageBox.warning(self, "Campos requeridos", "El nombre del producto es obligatorio.")
            return
        self.productos[idx] = data
        guardar_productos(self.productos)
        self.refresh_product_list()
        self.clear_form()

    def eliminar_producto(self):
        idx = self.lista_productos.currentRow()
        if idx < 0:
            QMessageBox.information(self, "Selecciona", "Elige un producto para eliminar.")
            return
        self.productos.pop(idx)
        guardar_productos(self.productos)
        self.refresh_product_list()
        self.clear_form()

    def refresh_product_list(self):
        self.lista_productos.clear()
        for p in self.productos:
            txt = f'{p.get("nombre", "")} - {p.get("sku", "")} - {p.get("categoria", "")}/{p.get("subcategoria", "")}'
            self.lista_productos.addItem(txt)

    def cargar_producto_en_formulario(self, idx):
        if idx < 0 or idx >= len(self.productos):
            self.clear_form()
            return
        p = self.productos[idx]
        self.sku_input.setText(p.get("sku", ""))
        self.nombre_combo.setCurrentText(p.get("nombre", ""))
        self.marca_combo.setCurrentText(p.get("marca", ""))
        self.tecnica_combo.setCurrentText(p.get("tecnica", ""))
        self.tamano_combo.setCurrentText(p.get("tamano", ""))
        self.color_combo.setCurrentText(p.get("color", ""))
        self.forma_combo.setCurrentText(p.get("forma", ""))
        self.diseno_input.setText(p.get("diseno", ""))
        self.categoria_combo.setCurrentText(p.get("categoria", ""))
        self.update_subcategorias()
        self.subcategoria_combo.setCurrentText(p.get("subcategoria", ""))

    def clear_form(self):
        self.sku_input.clear()
        self.nombre_combo.setCurrentIndex(0)
        self.marca_combo.setCurrentIndex(0)
        self.tecnica_combo.setCurrentIndex(0)
        self.tamano_combo.setCurrentIndex(0)
        self.color_combo.setCurrentIndex(0)
        self.forma_combo.setCurrentIndex(0)
        self.diseno_input.clear()
        self.categoria_combo.setCurrentIndex(0)
        self.update_subcategorias()
        self.subcategoria_combo.setCurrentIndex(0)

def obtener_productos():
    return cargar_productos()