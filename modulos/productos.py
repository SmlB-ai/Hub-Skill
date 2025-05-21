import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QHBoxLayout,
    QFormLayout, QComboBox, QMessageBox, QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt

DATA_DIR = "datos"
PRODUCTOS_FILE = os.path.join(DATA_DIR, "productos.json")
CATEGORIAS_FILE = os.path.join(DATA_DIR, "categorias.json")
MARCAS_FILE = os.path.join(DATA_DIR, "marcas.json")
NOMBRES_PRODUCTO_FILE = os.path.join(DATA_DIR, "nombres_producto.json")
TECNICAS_FILE = os.path.join(DATA_DIR, "tecnicas.json")
TAMANOS_FILE = os.path.join(DATA_DIR, "tamanos.json")
COLORES_FILE = os.path.join(DATA_DIR, "colores.json")
FORMAS_FILE = os.path.join(DATA_DIR, "formas.json")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

class ProductosWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Datos de Producto")
        self.setMinimumSize(950, 700)

        ensure_data_dir()
        self.productos = []
        self.categorias = {}
        self.marcas = []
        self.nombres_producto = []
        self.tecnicas = []
        self.tamanos = []
        self.colores = []
        self.formas = []

        self.load_data()
        self.init_ui()

    def load_json(self, file, default):
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        return default

    def save_json(self, file, data):
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        self.productos = self.load_json(PRODUCTOS_FILE, [])
        self.categorias = self.load_json(CATEGORIAS_FILE, {
            "Sin categoría": [],
            "Accesorios": [],
            "Bisutería y Joyería": [],
            "Bolsas Tote": [],
            "Decoración para Eventos": [],
            "Hogar": ["Cocina", "Accesorios y Organizadores"],
            "Tazas": ["Taza Blanca", "Taza Negra", "Termos"],
            "Decoración": ["Cuadros y Arte", "Lámparas e Iluminación", "Organizadores"],
            "Muebles": ["Camas y Cabeceras", "Mesas y Escritorios", "Organizadores y Estanterías", "Sillas y Bancos"],
            "Ofertas y Promociones": [],
            "Productos Digitales": [],
            "Ropa": ["Hombre", "Playeras", "Sudaderas", "Mujer", "Playeras", "Sudaderas"]
        })
        self.marcas = self.load_json(MARCAS_FILE, ["Sin marca"])
        self.nombres_producto = self.load_json(NOMBRES_PRODUCTO_FILE, ["Playera", "Taza", "Poster", "Sudadera"])
        self.tecnicas = self.load_json(TECNICAS_FILE, ["Sublimación", "DTF", "Vinil"])
        self.tamanos = self.load_json(TAMANOS_FILE, ["Chico", "Mediano", "Grande"])
        self.colores = self.load_json(COLORES_FILE, ["Blanco", "Negro", "Rojo"])
        self.formas = self.load_json(FORMAS_FILE, ["Redondo", "Rectangular", "Cuadrado"])

    def save_data(self):
        self.save_json(PRODUCTOS_FILE, self.productos)
        self.save_json(CATEGORIAS_FILE, self.categorias)
        self.save_json(MARCAS_FILE, self.marcas)
        self.save_json(NOMBRES_PRODUCTO_FILE, self.nombres_producto)
        self.save_json(TECNICAS_FILE, self.tecnicas)
        self.save_json(TAMANOS_FILE, self.tamanos)
        self.save_json(COLORES_FILE, self.colores)
        self.save_json(FORMAS_FILE, self.formas)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        title_label = QLabel("Datos de Producto")
        title_label.setStyleSheet("font-size: 22pt; font-weight: bold; margin-bottom: 15px;")
        main_layout.addWidget(title_label)

        # Lista de productos
        self.lista_productos = QListWidget()
        self.lista_productos.currentRowChanged.connect(self.cargar_producto_en_formulario)
        self.refresh_product_list()
        self.lista_productos.setMinimumHeight(180)
        main_layout.addWidget(self.lista_productos)

        # Formulario
        form = QFormLayout()

        self.marca_combo = QComboBox()
        self.marca_combo.addItems(self.marcas)
        btn_add_marca = QPushButton("+ Marca")
        btn_add_marca.setFixedWidth(80)
        btn_add_marca.clicked.connect(self.add_marca)
        h_marca = QHBoxLayout()
        h_marca.addWidget(self.marca_combo)
        h_marca.addWidget(btn_add_marca)

        self.producto_combo = QComboBox()
        self.producto_combo.addItems(self.nombres_producto)
        btn_add_producto = QPushButton("+ Producto")
        btn_add_producto.setFixedWidth(90)
        btn_add_producto.clicked.connect(self.add_producto)
        h_producto = QHBoxLayout()
        h_producto.addWidget(self.producto_combo)
        h_producto.addWidget(btn_add_producto)

        self.tecnica_combo = QComboBox()
        self.tecnica_combo.addItems(self.tecnicas)
        btn_add_tecnica = QPushButton("+ Técnica")
        btn_add_tecnica.setFixedWidth(90)
        btn_add_tecnica.clicked.connect(self.add_tecnica)
        h_tecnica = QHBoxLayout()
        h_tecnica.addWidget(self.tecnica_combo)
        h_tecnica.addWidget(btn_add_tecnica)

        self.tamano_combo = QComboBox()
        self.tamano_combo.addItems(self.tamanos)
        btn_add_tamano = QPushButton("+ Tamaño")
        btn_add_tamano.setFixedWidth(90)
        btn_add_tamano.clicked.connect(self.add_tamano)
        h_tamano = QHBoxLayout()
        h_tamano.addWidget(self.tamano_combo)
        h_tamano.addWidget(btn_add_tamano)

        self.color_combo = QComboBox()
        self.color_combo.addItems(self.colores)
        btn_add_color = QPushButton("+ Color")
        btn_add_color.setFixedWidth(80)
        btn_add_color.clicked.connect(self.add_color)
        h_color = QHBoxLayout()
        h_color.addWidget(self.color_combo)
        h_color.addWidget(btn_add_color)

        self.forma_combo = QComboBox()
        self.forma_combo.addItems(self.formas)
        btn_add_forma = QPushButton("+ Forma")
        btn_add_forma.setFixedWidth(80)
        btn_add_forma.clicked.connect(self.add_forma)
        h_forma = QHBoxLayout()
        h_forma.addWidget(self.forma_combo)
        h_forma.addWidget(btn_add_forma)

        self.diseno_input = QInputDialog()
        self.diseno_combo = QComboBox()
        self.diseno_combo.setEditable(True)  # Puedes editar manualmente el diseño
        # Por ahora no se guarda un catálogo de diseños

        self.categoria_combo = QComboBox()
        self.subcategoria_combo = QComboBox()
        self.refresh_categorias()
        self.categoria_combo.currentIndexChanged.connect(self.update_subcategorias)
        btn_add_cat = QPushButton("+ Cat.")
        btn_add_cat.setFixedWidth(60)
        btn_add_cat.clicked.connect(self.add_categoria)
        btn_add_subcat = QPushButton("+ Subcat.")
        btn_add_subcat.setFixedWidth(80)
        btn_add_subcat.clicked.connect(self.add_subcategoria)
        h_cat = QHBoxLayout()
        h_cat.addWidget(self.categoria_combo)
        h_cat.addWidget(btn_add_cat)
        h_subcat = QHBoxLayout()
        h_subcat.addWidget(self.subcategoria_combo)
        h_subcat.addWidget(btn_add_subcat)

        form.addRow("Marca:", h_marca)
        form.addRow("Producto:", h_producto)
        form.addRow("Técnica:", h_tecnica)
        form.addRow("Tamaño:", h_tamano)
        form.addRow("Color:", h_color)
        form.addRow("Forma:", h_forma)
        form.addRow("Diseño:", self.diseno_combo)
        form.addRow("Categoría:", h_cat)
        form.addRow("Subcategoría:", h_subcat)

        main_layout.addLayout(form)

        # Botones de acción
        button_layout = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar Producto")
        self.btn_editar = QPushButton("Editar Seleccionado")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_exportar = QPushButton("Exportar a CSV")

        self.btn_agregar.clicked.connect(self.agregar_producto)
        self.btn_editar.clicked.connect(self.editar_producto)
        self.btn_eliminar.clicked.connect(self.eliminar_producto)
        self.btn_exportar.clicked.connect(self.exportar_csv)
        button_layout.addWidget(self.btn_agregar)
        button_layout.addWidget(self.btn_editar)
        button_layout.addWidget(self.btn_eliminar)
        button_layout.addWidget(self.btn_exportar)
        main_layout.addLayout(button_layout)

    # Métodos para agregar nuevos valores a los combos y guardar
    def add_marca(self):
        text, ok = QInputDialog.getText(self, "Agregar Marca", "Nombre de nueva marca:")
        if ok and text and text not in self.marcas:
            self.marcas.append(text)
            self.marca_combo.addItem(text)
            self.save_data()

    def add_producto(self):
        text, ok = QInputDialog.getText(self, "Agregar Producto", "Nombre de nuevo producto:")
        if ok and text and text not in self.nombres_producto:
            self.nombres_producto.append(text)
            self.producto_combo.addItem(text)
            self.save_data()

    def add_tecnica(self):
        text, ok = QInputDialog.getText(self, "Agregar Técnica", "Nombre de nueva técnica:")
        if ok and text and text not in self.tecnicas:
            self.tecnicas.append(text)
            self.tecnica_combo.addItem(text)
            self.save_data()

    def add_tamano(self):
        text, ok = QInputDialog.getText(self, "Agregar Tamaño", "Nombre de nuevo tamaño:")
        if ok and text and text not in self.tamanos:
            self.tamanos.append(text)
            self.tamano_combo.addItem(text)
            self.save_data()

    def add_color(self):
        text, ok = QInputDialog.getText(self, "Agregar Color", "Nombre de nuevo color:")
        if ok and text and text not in self.colores:
            self.colores.append(text)
            self.color_combo.addItem(text)
            self.save_data()

    def add_forma(self):
        text, ok = QInputDialog.getText(self, "Agregar Forma", "Nombre de nueva forma:")
        if ok and text and text not in self.formas:
            self.formas.append(text)
            self.forma_combo.addItem(text)
            self.save_data()

    def refresh_product_list(self):
        self.lista_productos.clear()
        for i, p in enumerate(self.productos):
            txt = f'{p["marca"]} - {p["producto"]} - {p["categoria"]}/{p["subcategoria"]}'
            self.lista_productos.addItem(txt)

    def refresh_categorias(self):
        self.categoria_combo.clear()
        self.categoria_combo.addItems(self.categorias.keys())
        self.update_subcategorias()

    def update_subcategorias(self):
        categoria = self.categoria_combo.currentText()
        self.subcategoria_combo.clear()
        if categoria in self.categorias:
            self.subcategoria_combo.addItems(self.categorias[categoria])

    def add_categoria(self):
        text, ok = QInputDialog.getText(self, "Agregar categoría", "Nombre de nueva categoría:")
        if ok and text and text not in self.categorias:
            self.categorias[text] = []
            self.refresh_categorias()
            self.save_data()

    def add_subcategoria(self):
        categoria = self.categoria_combo.currentText()
        text, ok = QInputDialog.getText(self, "Agregar subcategoría", f"Subcategoría para {categoria}:")
        if ok and text and text not in self.categorias.get(categoria, []):
            self.categorias[categoria].append(text)
            self.update_subcategorias()
            self.save_data()

    def clear_form(self):
        self.marca_combo.setCurrentIndex(0)
        self.producto_combo.setCurrentIndex(0)
        self.tecnica_combo.setCurrentIndex(0)
        self.tamano_combo.setCurrentIndex(0)
        self.color_combo.setCurrentIndex(0)
        self.forma_combo.setCurrentIndex(0)
        self.diseno_combo.setEditText("")
        self.categoria_combo.setCurrentIndex(0)
        self.subcategoria_combo.setCurrentIndex(0)

    def get_form_data(self):
        return {
            "marca": self.marca_combo.currentText(),
            "producto": self.producto_combo.currentText(),
            "tecnica": self.tecnica_combo.currentText(),
            "tamano": self.tamano_combo.currentText(),
            "color": self.color_combo.currentText(),
            "forma": self.forma_combo.currentText(),
            "diseno": self.diseno_combo.currentText(),
            "categoria": self.categoria_combo.currentText(),
            "subcategoria": self.subcategoria_combo.currentText(),
        }

    def agregar_producto(self):
        data = self.get_form_data()
        # Validar campos obligatorios
        if not all([data["marca"], data["producto"]]):
            QMessageBox.warning(self, "Campos requeridos", "Marca y Producto son obligatorios.")
            return
        self.productos.append(data)
        self.save_data()
        self.refresh_product_list()
        self.clear_form()

    def editar_producto(self):
        idx = self.lista_productos.currentRow()
        if idx < 0:
            QMessageBox.information(self, "Selecciona", "Elige un producto para editar.")
            return
        data = self.get_form_data()
        if not all([data["marca"], data["producto"]]):
            QMessageBox.warning(self, "Campos requeridos", "Marca y Producto son obligatorios.")
            return
        self.productos[idx] = data
        self.save_data()
        self.refresh_product_list()
        self.clear_form()

    def eliminar_producto(self):
        idx = self.lista_productos.currentRow()
        if idx < 0:
            QMessageBox.information(self, "Selecciona", "Elige un producto para eliminar.")
            return
        self.productos.pop(idx)
        self.save_data()
        self.refresh_product_list()
        self.clear_form()

    def exportar_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportar CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            import csv
            with open(path, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Marca", "Producto", "Técnica", "Tamaño", "Color", "Forma", "Diseño", "Categoría", "Subcategoría"
                ])
                for p in self.productos:
                    writer.writerow([
                        p["marca"], p["producto"], p["tecnica"], p["tamano"],
                        p["color"], p["forma"], p["diseno"], p["categoria"], p["subcategoria"]
                    ])
            QMessageBox.information(self, "Exportado", "Productos exportados a CSV con éxito.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar el archivo:\n{e}")

    def cargar_producto_en_formulario(self, idx):
        if idx < 0 or idx >= len(self.productos):
            return
        p = self.productos[idx]
        self.marca_combo.setCurrentText(p.get("marca", ""))
        self.producto_combo.setCurrentText(p.get("producto", ""))
        self.tecnica_combo.setCurrentText(p.get("tecnica", ""))
        self.tamano_combo.setCurrentText(p.get("tamano", ""))
        self.color_combo.setCurrentText(p.get("color", ""))
        self.forma_combo.setCurrentText(p.get("forma", ""))
        self.diseno_combo.setEditText(p.get("diseno", ""))
        self.categoria_combo.setCurrentText(p.get("categoria", ""))
        # Actualiza subcategorías cuando cambia la categoría
        self.update_subcategorias()
        self.subcategoria_combo.setCurrentText(p.get("subcategoria", ""))