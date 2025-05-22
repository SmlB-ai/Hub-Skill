import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QFormLayout, QDoubleSpinBox, QMessageBox, QCheckBox, QSizePolicy, QFrame,
    QColorDialog, QDialog, QDialogButtonBox, QGridLayout
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize

DATA_DIR = "datos"
PRODUCTOS_FILE = os.path.join(DATA_DIR, "productos.json")
PRECIOS_FILE = os.path.join(DATA_DIR, "precios.json")
COLORES_FILE = os.path.join(DATA_DIR, "precios_colores.json")
IMAGES_ROOT = os.path.abspath("imagenes_productos")

# --- COLORES POR DEFECTO ---
DEFAULT_DESGLOSE_COLORS = {
    "subtotal": "#464646",
    "descuento": "#ff6f91",
    "subtotal_desc": "#5adbb5",
    "iva": "#6c8cff",
    "total_iva": "#ffc93c",
    "envio": "#ffa07a",
    "otros": "#b388ff",
    "final": "#1976d2"
}

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def cargar_productos():
    if os.path.exists(PRODUCTOS_FILE):
        with open(PRODUCTOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def cargar_precios():
    if os.path.exists(PRECIOS_FILE):
        with open(PRECIOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"global": {"iva": 16, "envio": 0, "descuento": 0, "precio_base": 0, "sumar_envio": False, "otros": 0, "sumar_otros": True},
            "categorias": {}, "productos": {}}

def guardar_precios(precios):
    with open(PRECIOS_FILE, "w", encoding="utf-8") as f:
        json.dump(precios, f, ensure_ascii=False, indent=2)

def obtener_imagen_principal(sku):
    carpeta = os.path.join(IMAGES_ROOT, sku)
    if not os.path.exists(carpeta):
        return ""
    files = [f for f in os.listdir(carpeta) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    if not files:
        return ""
    main = [f for f in files if "_main" in f]
    imgfile = main[0] if main else files[0]
    return os.path.join(carpeta, imgfile)

def cargar_colores_desglose():
    if os.path.exists(COLORES_FILE):
        with open(COLORES_FILE, "r", encoding="utf-8") as f:
            try:
                colores = json.load(f)
                return {**DEFAULT_DESGLOSE_COLORS, **colores}
            except Exception:
                return DEFAULT_DESGLOSE_COLORS.copy()
    return DEFAULT_DESGLOSE_COLORS.copy()

def guardar_colores_desglose(colores):
    with open(COLORES_FILE, "w", encoding="utf-8") as f:
        json.dump(colores, f, ensure_ascii=False, indent=2)

class DesgloseColorDialog(QDialog):
    def __init__(self, colores_actuales, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar colores de desglose")
        self.setModal(True)
        self.setMinimumWidth(370)
        self.colores = colores_actuales.copy()
        layout = QVBoxLayout(self)
        grid = QGridLayout()
        self.campos = {}
        labels = [
            ("subtotal", "Subtotal"),
            ("descuento", "Descuento"),
            ("subtotal_desc", "Subtotal con descuento"),
            ("iva", "IVA"),
            ("total_iva", "Total c/IVA"),
            ("envio", "Envío"),
            ("otros", "Otros"),
            ("final", "Precio final")
        ]
        for i, (key, label) in enumerate(labels):
            lbl = QLabel(label)
            btn = QPushButton()
            btn.setFixedSize(28, 28)
            btn.setStyleSheet(f"background:{self.colores[key]};border-radius:14px;")
            btn.clicked.connect(lambda _, k=key: self.cambiar_color(k))
            grid.addWidget(lbl, i, 0)
            grid.addWidget(btn, i, 1)
            self.campos[key] = btn
        layout.addLayout(grid)
        layout.addSpacing(8)
        self.btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)
        layout.addWidget(self.btn_box)

    def cambiar_color(self, key):
        color = QColorDialog.getColor()
        if color.isValid():
            hexcolor = color.name()
            self.campos[key].setStyleSheet(f"background:{hexcolor};border-radius:14px;")
            self.colores[key] = hexcolor

    def get_colores(self):
        return self.colores

class PreciosWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Precios y Dinero")
        self.setMinimumSize(500, 380)
        ensure_data_dir()
        self.productos = cargar_productos()
        self.precios = cargar_precios()
        self.colores_desglose = cargar_colores_desglose()
        self.init_ui()
        self.cargar_productos()

    def init_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(10, 10, 10, 10)
        main.setSpacing(5)

        # Barra superior: selector producto, refrescar y botón "Cambiar colores"
        barra = QHBoxLayout()
        lbl_prod = QLabel("Producto:")
        lbl_prod.setStyleSheet("font-weight:bold;")
        barra.addWidget(lbl_prod)
        self.producto_combo = QComboBox()
        self.producto_combo.setMinimumWidth(200)
        self.producto_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.producto_combo.currentIndexChanged.connect(self.mostrar_producto)
        barra.addWidget(self.producto_combo)
        barra.addStretch()
        self.btn_refresh = QPushButton("⟳")
        self.btn_refresh.setFixedWidth(32)
        self.btn_refresh.setToolTip("Refrescar productos y precios")
        self.btn_refresh.clicked.connect(self.refrescar_todo)
        barra.addWidget(self.btn_refresh)
        # Botón configurador de colores
        self.btn_config_colores = QPushButton("Cambiar colores")
        self.btn_config_colores.setFixedHeight(28)
        self.btn_config_colores.setStyleSheet("""
            QPushButton {
                background: #f8f8f8;
                color: #333;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 3px 13px;
                font-size: 10.5pt;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
        """)
        self.btn_config_colores.setToolTip("Configurar colores del desglose de precios")
        self.btn_config_colores.clicked.connect(self.abrir_config_colores)
        barra.addWidget(self.btn_config_colores)
        main.addLayout(barra)

        # Línea separadora fina
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        main.addWidget(sep)

        # Zona media: imagen + datos
        datos = QHBoxLayout()
        self.imagen_label = QLabel()
        self.imagen_label.setFixedSize(54, 54)
        self.imagen_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.imagen_label.setStyleSheet("border-radius:4px; background:#f2f2f2;")
        datos.addWidget(self.imagen_label)

        datos_form = QVBoxLayout()
        self.info_label = QLabel("Tipo: ---  |  Categoría: ---")
        self.info_label.setStyleSheet("font-size:10pt;font-weight:bold;")
        datos_form.addWidget(self.info_label)

        frm = QFormLayout()
        frm.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        frm.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        frm.setHorizontalSpacing(10)
        frm.setVerticalSpacing(4)
        self.precio_base_spin = QDoubleSpinBox()
        self.precio_base_spin.setRange(0, 100000)
        self.precio_base_spin.setPrefix("$")
        self.precio_base_spin.setDecimals(2)
        self.precio_base_spin.setMaximumWidth(110)
        frm.addRow("Base:", self.precio_base_spin)

        self.descuento_spin = QDoubleSpinBox()
        self.descuento_spin.setRange(0, 100)
        self.descuento_spin.setSuffix(" %")
        self.descuento_spin.setDecimals(2)
        self.descuento_spin.setMaximumWidth(85)
        frm.addRow("Desc.:", self.descuento_spin)

        self.iva_spin = QDoubleSpinBox()
        self.iva_spin.setRange(0, 100)
        self.iva_spin.setSuffix(" %")
        self.iva_spin.setDecimals(2)
        self.iva_spin.setMaximumWidth(85)
        frm.addRow("IVA:", self.iva_spin)

        envio_hbox = QHBoxLayout()
        self.envio_spin = QDoubleSpinBox()
        self.envio_spin.setRange(0, 100000)
        self.envio_spin.setPrefix("$")
        self.envio_spin.setDecimals(2)
        self.envio_spin.setMaximumWidth(85)
        self.envio_checkbox = QCheckBox("Sumar")
        self.envio_checkbox.setChecked(False)
        self.envio_checkbox.toggled.connect(self.actualizar_desglose)
        envio_hbox.addWidget(self.envio_spin)
        envio_hbox.addWidget(self.envio_checkbox)
        frm.addRow("Envío:", envio_hbox)

        otros_hbox = QHBoxLayout()
        self.otros_spin = QDoubleSpinBox()
        self.otros_spin.setRange(0, 100000)
        self.otros_spin.setPrefix("$")
        self.otros_spin.setDecimals(2)
        self.otros_spin.setMaximumWidth(85)
        self.otros_checkbox = QCheckBox("Sumar")
        self.otros_checkbox.setChecked(True)
        self.otros_checkbox.toggled.connect(self.actualizar_desglose)
        otros_hbox.addWidget(self.otros_spin)
        otros_hbox.addWidget(self.otros_checkbox)
        frm.addRow("Otros:", otros_hbox)

        datos_form.addLayout(frm)
        datos.addLayout(datos_form)
        main.addLayout(datos)

        # Fuente de parámetros
        self.fuente_label = QLabel()
        self.fuente_label.setStyleSheet("color: #888; font-style: italic; margin-bottom:1px; font-size:9.5pt;")
        main.addWidget(self.fuente_label)

        # Desglose tipo factura
        self.desglose_label = QLabel()
        self.desglose_label.setWordWrap(True)
        self.desglose_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.desglose_label.setStyleSheet("""
            font-size: 12.5pt; font-weight: 500; color: #232323;
            margin: 3px 0 6px 0;
        """)
        main.addWidget(self.desglose_label)

        # Precio final grande, sin fondo, claro
        self.precio_final_label = QLabel()
        self.precio_final_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.precio_final_label.setStyleSheet("""
            font-size: 22pt; font-weight: bold;
            color: #1565c0; margin: 0 0 4px 0;
        """)
        main.addWidget(self.precio_final_label)

        # Botones para guardar
        btns = QHBoxLayout()
        self.btn_guardar_prod = QPushButton("Guardar producto")
        self.btn_guardar_prod.setStyleSheet("padding:5px 13px;")
        self.btn_guardar_prod.clicked.connect(self.guardar_precio_producto)
        btns.addWidget(self.btn_guardar_prod)
        self.btn_guardar_cat = QPushButton("Guardar categoría")
        self.btn_guardar_cat.setStyleSheet("padding:5px 13px;")
        self.btn_guardar_cat.clicked.connect(self.guardar_precio_categoria)
        btns.addWidget(self.btn_guardar_cat)
        self.btn_guardar_global = QPushButton("Guardar global")
        self.btn_guardar_global.setStyleSheet("padding:5px 13px;")
        self.btn_guardar_global.clicked.connect(self.guardar_precio_global)
        btns.addWidget(self.btn_guardar_global)
        btns.addStretch()
        main.addLayout(btns)

        # Conecta los campos para actualizar desglose en tiempo real
        self.precio_base_spin.valueChanged.connect(self.actualizar_desglose)
        self.descuento_spin.valueChanged.connect(self.actualizar_desglose)
        self.iva_spin.valueChanged.connect(self.actualizar_desglose)
        self.envio_spin.valueChanged.connect(self.actualizar_desglose)
        self.otros_spin.valueChanged.connect(self.actualizar_desglose)
        self.envio_checkbox.stateChanged.connect(self.actualizar_desglose)
        self.otros_checkbox.stateChanged.connect(self.actualizar_desglose)

    def abrir_config_colores(self):
        dlg = DesgloseColorDialog(self.colores_desglose, self)
        if dlg.exec():
            self.colores_desglose = dlg.get_colores()
            guardar_colores_desglose(self.colores_desglose)
            self.actualizar_desglose()

    def refrescar_todo(self):
        self.productos = cargar_productos()
        self.precios = cargar_precios()
        self.cargar_productos()

    def cargar_productos(self):
        self.producto_combo.clear()
        for prod in self.productos:
            sku = prod.get("sku", "")
            nombre = prod.get("nombre", "")
            cat = prod.get("categoria", "")
            item_text = f"{sku} | {nombre} [{cat}]"
            self.producto_combo.addItem(item_text, userData=sku)
        if self.productos:
            self.producto_combo.setCurrentIndex(0)
            self.mostrar_producto(0)
        else:
            self.limpiar_campos()

    def limpiar_campos(self):
        self.imagen_label.clear()
        self.info_label.setText("")
        self.fuente_label.setText("")
        self.precio_base_spin.setValue(0)
        self.descuento_spin.setValue(0)
        self.iva_spin.setValue(0)
        self.envio_spin.setValue(0)
        self.envio_checkbox.setChecked(False)
        self.otros_spin.setValue(0)
        self.otros_checkbox.setChecked(True)
        self.desglose_label.setText("")
        self.precio_final_label.setText("")

    def mostrar_producto(self, idx):
        if idx < 0 or idx >= len(self.productos):
            self.limpiar_campos()
            return
        prod = self.productos[idx]
        sku = prod.get("sku", "")
        nombre = prod.get("nombre", "")
        cat = prod.get("categoria", "")
        self.info_label.setText(f"Nombre: {nombre} | Categoría: {cat}")

        # Imagen principal
        img_path = obtener_imagen_principal(sku)
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path).scaled(54, 54, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.imagen_label.setPixmap(pixmap)
        else:
            self.imagen_label.clear()

        # Buscar precios según prioridad: producto > categoría > global
        pprod = self.precios.get("productos", {}).get(sku)
        pcat = self.precios.get("categorias", {}).get(cat)
        pglob = self.precios.get("global", {})

        otros = 0
        fuente = ""
        if pprod:
            self.precio_base_spin.setValue(pprod.get("precio_base", 0))
            self.descuento_spin.setValue(pprod.get("descuento", 0))
            self.iva_spin.setValue(pprod.get("iva", pcat.get("iva", pglob.get("iva", 0)) if pcat else pglob.get("iva", 0)))
            self.envio_spin.setValue(pprod.get("envio", pcat.get("envio", pglob.get("envio", 0)) if pcat else pglob.get("envio", 0)))
            self.envio_checkbox.setChecked(pprod.get("sumar_envio", False))
            otros = pprod.get("otros", 0)
            self.otros_spin.setValue(otros)
            self.otros_checkbox.setChecked(pprod.get("sumar_otros", True))
            fuente = "Parámetros propios del producto."
        elif pcat:
            self.precio_base_spin.setValue(pcat.get("precio_base", 0))
            self.descuento_spin.setValue(pcat.get("descuento", 0))
            self.iva_spin.setValue(pcat.get("iva", pglob.get("iva", 0)))
            self.envio_spin.setValue(pcat.get("envio", pglob.get("envio", 0)))
            self.envio_checkbox.setChecked(pcat.get("sumar_envio", False))
            otros = pcat.get("otros", 0)
            self.otros_spin.setValue(otros)
            self.otros_checkbox.setChecked(pcat.get("sumar_otros", True))
            fuente = "Parámetros heredados de la CATEGORÍA."
        elif pglob:
            self.precio_base_spin.setValue(pglob.get("precio_base", 0))
            self.descuento_spin.setValue(pglob.get("descuento", 0))
            self.iva_spin.setValue(pglob.get("iva", 0))
            self.envio_spin.setValue(pglob.get("envio", 0))
            self.envio_checkbox.setChecked(pglob.get("sumar_envio", False))
            otros = pglob.get("otros", 0)
            self.otros_spin.setValue(otros)
            self.otros_checkbox.setChecked(pglob.get("sumar_otros", True))
            fuente = "Parámetros globales."
        else:
            self.precio_base_spin.setValue(0)
            self.descuento_spin.setValue(0)
            self.iva_spin.setValue(0)
            self.envio_spin.setValue(0)
            self.envio_checkbox.setChecked(False)
            self.otros_spin.setValue(0)
            self.otros_checkbox.setChecked(True)
            fuente = "Sin parámetros asignados todavía."

        self.fuente_label.setText(fuente)
        self.actualizar_desglose()

    def actualizar_desglose(self):
        c = self.colores_desglose
        precio_base = self.precio_base_spin.value()
        descuento = self.descuento_spin.value()
        iva = self.iva_spin.value()
        envio = self.envio_spin.value()
        otros = self.otros_spin.value()
        sumar_envio = self.envio_checkbox.isChecked()
        sumar_otros = self.otros_checkbox.isChecked()

        precio_desc = precio_base * (1 - descuento / 100)
        monto_desc = precio_base - precio_desc
        precio_iva = precio_desc * (1 + iva / 100)
        monto_iva = precio_iva - precio_desc
        suma = precio_desc + monto_iva
        monto_envio = envio if sumar_envio else 0
        monto_otros = otros if sumar_otros else 0
        precio_final = precio_iva + monto_envio + monto_otros

        # Desglose tipo factura con colores personalizados
        desglose = f"""<span style='color:{c["subtotal"]};'>
        <b>Subtotal:</b> ${precio_base:,.2f}<br>
        <span style='color:{c["descuento"]};'>- Descuento:</span> ${monto_desc:,.2f} <span style="font-size:10pt;">({descuento:.2f}%)</span><br>
        <span style='color:{c["subtotal_desc"]};'>= Subtotal con desc.:</span> ${precio_desc:,.2f}<br>
        <span style='color:{c["iva"]};'>+ IVA:</span> ${monto_iva:,.2f} <span style="font-size:10pt;">({iva:.2f}%)</span><br>
        <span style='color:{c["total_iva"]};'>= Total c/IVA:</span> ${precio_iva:,.2f}<br>"""
        if sumar_envio:
            desglose += f"<span style='color:{c['envio']};'>+ Envío:</span> ${envio:,.2f}<br>"
        else:
            desglose += f"<span style='color:{c['envio']};'>Envío (no sumado):</span> ${envio:,.2f}<br>"
        if sumar_otros:
            desglose += f"<span style='color:{c['otros']};'>+ Otros:</span> ${otros:,.2f}<br>"
        else:
            desglose += f"<span style='color:{c['otros']};'>Otros (no sumado):</span> ${otros:,.2f}<br>"
        desglose += "</span>"
        self.desglose_label.setText(desglose)

        self.precio_final_label.setText(
            f"Precio final:  <span style='color:{c['final']}'><b>${precio_final:,.2f}</b></span>"
        )

    def guardar_precio_producto(self):
        idx = self.producto_combo.currentIndex()
        if idx < 0 or idx >= len(self.productos):
            return
        prod = self.productos[idx]
        sku = prod.get("sku", "")
        self.precios.setdefault("productos", {})[sku] = {
            "precio_base": self.precio_base_spin.value(),
            "descuento": self.descuento_spin.value(),
            "iva": self.iva_spin.value(),
            "envio": self.envio_spin.value(),
            "sumar_envio": self.envio_checkbox.isChecked(),
            "otros": self.otros_spin.value(),
            "sumar_otros": self.otros_checkbox.isChecked()
        }
        guardar_precios(self.precios)
        QMessageBox.information(self, "Guardado", "Parámetros guardados para este producto.")
        self.mostrar_producto(idx)

    def guardar_precio_categoria(self):
        idx = self.producto_combo.currentIndex()
        if idx < 0 or idx >= len(self.productos):
            return
        prod = self.productos[idx]
        cat = prod.get("categoria", "")
        self.precios.setdefault("categorias", {})[cat] = {
            "precio_base": self.precio_base_spin.value(),
            "descuento": self.descuento_spin.value(),
            "iva": self.iva_spin.value(),
            "envio": self.envio_spin.value(),
            "sumar_envio": self.envio_checkbox.isChecked(),
            "otros": self.otros_spin.value(),
            "sumar_otros": self.otros_checkbox.isChecked()
        }
        guardar_precios(self.precios)
        QMessageBox.information(self, "Guardado", f"Parámetros guardados para la categoría '{cat}'.")
        self.mostrar_producto(idx)

    def guardar_precio_global(self):
        self.precios["global"] = {
            "precio_base": self.precio_base_spin.value(),
            "descuento": self.descuento_spin.value(),
            "iva": self.iva_spin.value(),
            "envio": self.envio_spin.value(),
            "sumar_envio": self.envio_checkbox.isChecked(),
            "otros": self.otros_spin.value(),
            "sumar_otros": self.otros_checkbox.isChecked()
        }
        guardar_precios(self.precios)
        QMessageBox.information(self, "Guardado", "Parámetros globales guardados.")
        idx = self.producto_combo.currentIndex()
        self.mostrar_producto(idx)