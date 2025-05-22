import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QFormLayout, QDoubleSpinBox, QMessageBox, QGroupBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

DATA_DIR = "datos"
PRODUCTOS_FILE = os.path.join(DATA_DIR, "productos.json")
MEDIDAS_FILE = os.path.join(DATA_DIR, "medidas.json")
IMAGES_ROOT = os.path.abspath("imagenes_productos")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def cargar_productos():
    if os.path.exists(PRODUCTOS_FILE):
        with open(PRODUCTOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def cargar_medidas():
    if os.path.exists(MEDIDAS_FILE):
        with open(MEDIDAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"categorias": {}, "tipos": {}, "productos": {}}

def guardar_medidas(medidas):
    with open(MEDIDAS_FILE, "w", encoding="utf-8") as f:
        json.dump(medidas, f, ensure_ascii=False, indent=2)

def obtener_imagen_principal(sku):
    carpeta = os.path.join(IMAGES_ROOT, sku)
    if not os.path.exists(carpeta):
        return ""
    files = [f for f in os.listdir(carpeta) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    if not files:
        return ""
    # Busca la que contenga '_main', si no la primera
    main = [f for f in files if "_main" in f]
    imgfile = main[0] if main else files[0]
    return os.path.join(carpeta, imgfile)

class MedidasWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Asignar Medidas a Productos")
        self.setMinimumSize(700, 450)
        ensure_data_dir()
        self.productos = cargar_productos()
        self.medidas = cargar_medidas()
        self.init_ui()
        self.cargar_productos()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Selector producto
        prod_layout = QHBoxLayout()
        prod_layout.addWidget(QLabel("Producto:"))
        self.producto_combo = QComboBox()
        self.producto_combo.currentIndexChanged.connect(self.mostrar_producto)
        prod_layout.addWidget(self.producto_combo)
        layout.addLayout(prod_layout)

        # Imagen principal
        self.imagen_label = QLabel()
        self.imagen_label.setFixedHeight(120)
        self.imagen_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.imagen_label)

        # Datos del producto
        self.info_label = QLabel("Tipo: ---  |  Categoría: ---")
        layout.addWidget(self.info_label)

        # Formulario de medidas
        form_group = QGroupBox("Medidas físicas")
        form = QFormLayout()
        self.ancho_spin = QDoubleSpinBox()
        self.ancho_spin.setRange(0, 1000)
        self.ancho_spin.setDecimals(2)
        form.addRow("Ancho (cm):", self.ancho_spin)
        self.alto_spin = QDoubleSpinBox()
        self.alto_spin.setRange(0, 1000)
        self.alto_spin.setDecimals(2)
        form.addRow("Alto (cm):", self.alto_spin)
        self.largo_spin = QDoubleSpinBox()
        self.largo_spin.setRange(0, 1000)
        self.largo_spin.setDecimals(2)
        form.addRow("Largo (cm):", self.largo_spin)
        self.peso_spin = QDoubleSpinBox()
        self.peso_spin.setRange(0, 1000)
        self.peso_spin.setDecimals(3)
        form.addRow("Peso (kg):", self.peso_spin)
        form_group.setLayout(form)
        layout.addWidget(form_group)

        # ¿De dónde provienen las medidas?
        self.fuente_label = QLabel()
        self.fuente_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.fuente_label)

        # Botones para guardar
        btns = QHBoxLayout()
        self.btn_guardar_prod = QPushButton("Guardar SOLO para este producto")
        self.btn_guardar_prod.clicked.connect(self.guardar_medidas_producto)
        btns.addWidget(self.btn_guardar_prod)
        self.btn_guardar_tipo = QPushButton("Guardar para tipo")
        self.btn_guardar_tipo.clicked.connect(self.guardar_medidas_tipo)
        btns.addWidget(self.btn_guardar_tipo)
        self.btn_guardar_cat = QPushButton("Guardar para categoría")
        self.btn_guardar_cat.clicked.connect(self.guardar_medidas_categoria)
        btns.addWidget(self.btn_guardar_cat)
        layout.addLayout(btns)

        # Botón para recargar productos/medidas
        btns_refresh = QHBoxLayout()
        self.btn_refresh = QPushButton("Refrescar productos y medidas")
        self.btn_refresh.clicked.connect(self.refrescar_todo)
        btns_refresh.addWidget(self.btn_refresh)
        layout.addLayout(btns_refresh)

    def refrescar_todo(self):
        self.productos = cargar_productos()
        self.medidas = cargar_medidas()
        self.cargar_productos()

    def cargar_productos(self):
        self.producto_combo.clear()
        for prod in self.productos:
            sku = prod.get("sku", "")
            nombre = prod.get("nombre", "")
            tipo = prod.get("nombre", "")  # Puedes cambiar esto si tienes un campo 'tipo'
            cat = prod.get("categoria", "")
            item_text = f"{sku} | {nombre} [{cat}]"
            self.producto_combo.addItem(item_text, userData=sku)
        if self.productos:
            self.producto_combo.setCurrentIndex(0)
            self.mostrar_producto(0)
        else:
            self.imagen_label.clear()
            self.info_label.setText("")
            self.fuente_label.setText("")
            self.ancho_spin.setValue(0)
            self.alto_spin.setValue(0)
            self.largo_spin.setValue(0)
            self.peso_spin.setValue(0)

    def mostrar_producto(self, idx):
        if idx < 0 or idx >= len(self.productos):
            self.imagen_label.clear()
            self.info_label.setText("")
            self.fuente_label.setText("")
            self.ancho_spin.setValue(0)
            self.alto_spin.setValue(0)
            self.largo_spin.setValue(0)
            self.peso_spin.setValue(0)
            return
        prod = self.productos[idx]
        sku = prod.get("sku", "")
        tipo = prod.get("nombre", "")  # O el campo que uses como tipo
        cat = prod.get("categoria", "")
        self.info_label.setText(f"Tipo: {tipo}  |  Categoría: {cat}")

        # Imagen principal
        img_path = obtener_imagen_principal(sku)
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path).scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.imagen_label.setPixmap(pixmap)
        else:
            self.imagen_label.clear()

        # Buscar medidas según prioridad: producto > tipo > categoría
        mprod = self.medidas.get("productos", {}).get(sku)
        mtipo = self.medidas.get("tipos", {}).get(tipo)
        mcat = self.medidas.get("categorias", {}).get(cat)
        if mprod:
            self.ancho_spin.setValue(mprod.get("ancho", 0))
            self.alto_spin.setValue(mprod.get("alto", 0))
            self.largo_spin.setValue(mprod.get("largo", 0))
            self.peso_spin.setValue(mprod.get("peso", 0))
            self.fuente_label.setText("Medidas propias del producto.")
        elif mtipo:
            self.ancho_spin.setValue(mtipo.get("ancho", 0))
            self.alto_spin.setValue(mtipo.get("alto", 0))
            self.largo_spin.setValue(mtipo.get("largo", 0))
            self.peso_spin.setValue(mtipo.get("peso", 0))
            self.fuente_label.setText("Medidas heredadas del TIPO.")
        elif mcat:
            self.ancho_spin.setValue(mcat.get("ancho", 0))
            self.alto_spin.setValue(mcat.get("alto", 0))
            self.largo_spin.setValue(mcat.get("largo", 0))
            self.peso_spin.setValue(mcat.get("peso", 0))
            self.fuente_label.setText("Medidas heredadas de la CATEGORÍA.")
        else:
            self.ancho_spin.setValue(0)
            self.alto_spin.setValue(0)
            self.largo_spin.setValue(0)
            self.peso_spin.setValue(0)
            self.fuente_label.setText("Sin medidas asignadas todavía.")

    def guardar_medidas_producto(self):
        idx = self.producto_combo.currentIndex()
        if idx < 0 or idx >= len(self.productos):
            return
        prod = self.productos[idx]
        sku = prod.get("sku", "")
        self.medidas.setdefault("productos", {})[sku] = {
            "ancho": self.ancho_spin.value(),
            "alto": self.alto_spin.value(),
            "largo": self.largo_spin.value(),
            "peso": self.peso_spin.value()
        }
        guardar_medidas(self.medidas)
        QMessageBox.information(self, "Guardado", "Medidas guardadas SOLO para este producto.")
        self.mostrar_producto(idx)

    def guardar_medidas_tipo(self):
        idx = self.producto_combo.currentIndex()
        if idx < 0 or idx >= len(self.productos):
            return
        prod = self.productos[idx]
        tipo = prod.get("nombre", "")  # O el campo que uses como tipo
        self.medidas.setdefault("tipos", {})[tipo] = {
            "ancho": self.ancho_spin.value(),
            "alto": self.alto_spin.value(),
            "largo": self.largo_spin.value(),
            "peso": self.peso_spin.value()
        }
        guardar_medidas(self.medidas)
        QMessageBox.information(self, "Guardado", f"Medidas guardadas para el tipo '{tipo}'.")
        self.mostrar_producto(idx)

    def guardar_medidas_categoria(self):
        idx = self.producto_combo.currentIndex()
        if idx < 0 or idx >= len(self.productos):
            return
        prod = self.productos[idx]
        cat = prod.get("categoria", "")
        self.medidas.setdefault("categorias", {})[cat] = {
            "ancho": self.ancho_spin.value(),
            "alto": self.alto_spin.value(),
            "largo": self.largo_spin.value(),
            "peso": self.peso_spin.value()
        }
        guardar_medidas(self.medidas)
        QMessageBox.information(self, "Guardado", f"Medidas guardadas para la categoría '{cat}'.")
        self.mostrar_producto(idx)