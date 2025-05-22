import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
    QMessageBox, QFrame, QFileDialog, QComboBox, QTabWidget, QTableWidget, QTableWidgetItem, QCheckBox, QDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

DATA_DIR = "datos"
DESCRIPCIONES_FILE = os.path.join(DATA_DIR, "descripciones.json")
PRODUCTOS_FILE = os.path.join(DATA_DIR, "productos.json")
IMAGES_ROOT = os.path.abspath("imagenes_productos")
NOTACOMPRA_FILE = os.path.join(DATA_DIR, "nota_compra_global.txt")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def cargar_descripciones():
    if os.path.exists(DESCRIPCIONES_FILE):
        with open(DESCRIPCIONES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_descripciones(data):
    with open(DESCRIPCIONES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cargar_productos():
    if os.path.exists(PRODUCTOS_FILE):
        with open(PRODUCTOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def obtener_categorias_de_productos(productos):
    categorias = set()
    for prod in productos:
        cat = prod.get("categoria", "")
        if cat:
            categorias.add(cat)
    return sorted(list(categorias))

def cargar_nota_compra_global():
    if os.path.exists(NOTACOMPRA_FILE):
        with open(NOTACOMPRA_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def guardar_nota_compra_global(text):
    ensure_data_dir()
    with open(NOTACOMPRA_FILE, "w", encoding="utf-8") as f:
        f.write(text)

def obtener_imagenes_producto(sku):
    carpeta = os.path.join(IMAGES_ROOT, sku)
    if not os.path.exists(carpeta):
        return []
    files = [f for f in os.listdir(carpeta) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    return [os.path.join(carpeta, f) for f in sorted(files)]

class NotaCompraConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Nota de Compra Global")
        self.setMinimumSize(450, 240)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Nota de compra global (aparecerá en todos los productos):"))
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(cargar_nota_compra_global())
        self.text_edit.setMinimumHeight(100)
        layout.addWidget(self.text_edit)
        btns = QHBoxLayout()
        btn_guardar = QPushButton("Guardar y cerrar")
        btn_guardar.clicked.connect(self.aceptar)
        btns.addWidget(btn_guardar)
        btns.addStretch()
        layout.addLayout(btns)

    def aceptar(self):
        guardar_nota_compra_global(self.text_edit.toPlainText())
        self.accept()

class DescripcionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Descripción y Contenido")
        self.setMinimumSize(1100, 700)
        ensure_data_dir()
        self.descripciones = cargar_descripciones()
        self.productos = cargar_productos()
        self.current_sku = None
        self.categorias = obtener_categorias_de_productos(self.productos)
        self.init_ui()

    def init_ui(self):
        main = QHBoxLayout(self)
        main.setContentsMargins(12, 10, 12, 10)
        main.setSpacing(10)

        # --- IZQUIERDA: Tabs de edición ---
        left = QVBoxLayout()
        self.tabs = QTabWidget()

        # --- TAB DESCRIPCIONES ---
        tab_desc = QWidget()
        desc_layout = QVBoxLayout(tab_desc)
        # Selector SKU/producto y muestra ID
        prod_row = QHBoxLayout()
        lblsku = QLabel("Producto / SKU:")
        lblsku.setStyleSheet("font-weight:bold;")
        prod_row.addWidget(lblsku)
        self.sku_combo = QComboBox()
        self.sku_combo.setEditable(True)
        self.sku_combo.setMinimumWidth(220)
        self.sku_combo.currentIndexChanged.connect(self.cargar_para_sku_combo)
        prod_row.addWidget(self.sku_combo)
        self.lbl_id = QLabel("ID Woo: -")
        self.lbl_id.setStyleSheet("font-size:10pt;color:#888;margin-left:12px;")
        prod_row.addWidget(self.lbl_id)
        btn_nota = QPushButton("Configurar nota de compra global")
        btn_nota.clicked.connect(self.configurar_nota_compra)
        prod_row.addWidget(btn_nota)
        desc_layout.addLayout(prod_row)

        # Descripción corta (HTML)
        desc_layout.addWidget(QLabel("Descripción corta (HTML):"))
        self.desc_corta_edit = QTextEdit()
        self.desc_corta_edit.setPlaceholderText("HTML soportado. Ej: <ul><li>Item</li></ul>")
        self.desc_corta_edit.setMinimumHeight(40)
        desc_layout.addWidget(self.desc_corta_edit)
        # Botón aplicar a toda la categoría
        row_corta = QHBoxLayout()
        self.btn_aplicar_corta_cat = QPushButton("Aplicar a categoría")
        self.btn_aplicar_corta_cat.setToolTip("Aplica esta descripción corta a todos los productos de la misma categoría, excepto los que tienen personalizada.")
        self.btn_aplicar_corta_cat.clicked.connect(lambda: self.aplicar_a_categoria('desc_corta'))
        row_corta.addStretch()
        row_corta.addWidget(self.btn_aplicar_corta_cat)
        desc_layout.addLayout(row_corta)

        # Descripción larga (HTML)
        desc_layout.addWidget(QLabel("Descripción larga (HTML):"))
        self.desc_larga_edit = QTextEdit()
        self.desc_larga_edit.setPlaceholderText("Puedes usar cualquier HTML válido aquí.")
        self.desc_larga_edit.setMinimumHeight(70)
        desc_layout.addWidget(self.desc_larga_edit)
        # Botón aplicar a toda la categoría
        row_larga = QHBoxLayout()
        self.btn_aplicar_larga_cat = QPushButton("Aplicar a categoría")
        self.btn_aplicar_larga_cat.setToolTip("Aplica esta descripción larga a todos los productos de la misma categoría, excepto los que tienen personalizada.")
        self.btn_aplicar_larga_cat.clicked.connect(lambda: self.aplicar_a_categoria('desc_larga'))
        row_larga.addStretch()
        row_larga.addWidget(self.btn_aplicar_larga_cat)
        desc_layout.addLayout(row_larga)

        tab_desc.setLayout(desc_layout)
        self.tabs.addTab(tab_desc, "Descripciones")

        # --- TAB CATEGORÍAS, ETIQUETAS, ENVÍO ---
        tab_tax = QWidget()
        tax_layout = QVBoxLayout(tab_tax)
        tax_layout.addWidget(QLabel("Categorías (separadas por coma, jerarquía con '>')"))
        self.categorias_edit = QLineEdit()
        self.categorias_edit.setPlaceholderText("Ej: Hogar > Cocina, Hogar > Cocina > Tazas")
        tax_layout.addWidget(self.categorias_edit)
        tax_layout.addWidget(QLabel("Etiquetas (tags, separadas por coma)"))
        self.etiquetas_edit = QLineEdit()
        self.etiquetas_edit.setPlaceholderText("Ej: taza, cerámica, regalo, café")
        tax_layout.addWidget(self.etiquetas_edit)
        tax_layout.addWidget(QLabel("Clase de envío"))
        self.clase_envio_edit = QLineEdit()
        self.clase_envio_edit.setPlaceholderText("Ejemplo: Ligeros, Grandes")
        tax_layout.addWidget(self.clase_envio_edit)
        tab_tax.setLayout(tax_layout)
        self.tabs.addTab(tab_tax, "Categorías y Envío")

        # --- TAB META EXTRA ---
        tab_meta = QWidget()
        meta_layout = QVBoxLayout(tab_meta)
        meta_layout.addWidget(QLabel("Meta extra WooCommerce (clave/valor):"))
        self.meta_table = QTableWidget(0, 2)
        self.meta_table.setHorizontalHeaderLabels(["Clave", "Valor"])
        self.meta_table.horizontalHeader().setStretchLastSection(True)
        meta_layout.addWidget(self.meta_table)
        meta_btns = QHBoxLayout()
        btn_add_meta = QPushButton("+ Meta")
        btn_add_meta.clicked.connect(self.agregar_meta)
        btn_del_meta = QPushButton("- Meta")
        btn_del_meta.clicked.connect(self.eliminar_meta)
        meta_btns.addWidget(btn_add_meta)
        meta_btns.addWidget(btn_del_meta)
        meta_btns.addStretch()
        meta_layout.addLayout(meta_btns)
        tab_meta.setLayout(meta_layout)
        self.tabs.addTab(tab_meta, "Meta extra")

        left.addWidget(self.tabs)

        # Botones guardar/exportar
        btns = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.guardar)
        btns.addWidget(self.btn_guardar)
        self.btn_exportar = QPushButton("Exportar HTML WooCommerce")
        self.btn_exportar.clicked.connect(self.exportar_html)
        btns.addWidget(self.btn_exportar)
        btns.addStretch()
        left.addLayout(btns)
        left.addStretch()
        main.addLayout(left, 3)

        # --- Derecha: PREVIEW HTML RENDER + imágenes ---
        right = QVBoxLayout()
        right.addWidget(QLabel("<b>Vista previa (render HTML e imágenes)</b>"))
        self.preview_html = QTextEdit()
        self.preview_html.setReadOnly(True)
        self.preview_html.setMinimumWidth(420)
        self.preview_html.setMinimumHeight(480)
        self.preview_html.setStyleSheet("background:#fafcff; border:1px solid #d8e0e8; border-radius:7px; padding:8px; font-size:11.5pt;")
        right.addWidget(self.preview_html)
        main.addLayout(right, 4)

        self.llenar_sku_combo()
        self.desc_corta_edit.textChanged.connect(self.actualizar_preview)
        self.desc_larga_edit.textChanged.connect(self.actualizar_preview)
        self.categorias_edit.textChanged.connect(self.actualizar_preview)
        self.etiquetas_edit.textChanged.connect(self.actualizar_preview)
        self.clase_envio_edit.textChanged.connect(self.actualizar_preview)
        self.meta_table.cellChanged.connect(self.actualizar_preview)

    def configurar_nota_compra(self):
        dlg = NotaCompraConfigDialog(self)
        if dlg.exec():
            self.actualizar_preview()

    def aplicar_a_categoria(self, campo):
        if not self.current_sku:
            QMessageBox.warning(self, "SKU faltante", "Selecciona un producto para identificar la categoría.")
            return
        # Encuentra la categoría del producto actual
        prod = next((p for p in self.productos if p.get("sku") == self.current_sku), None)
        if not prod or not prod.get("categoria"):
            QMessageBox.warning(self, "Categoría faltante", "El producto seleccionado no tiene categoría.")
            return
        categoria = prod.get("categoria")
        value = ""
        if campo == "desc_corta":
            value = self.desc_corta_edit.toPlainText().strip()
        elif campo == "desc_larga":
            value = self.desc_larga_edit.toPlainText().strip()
        else:
            return
        if not value:
            QMessageBox.warning(self, "Campo vacío", "No hay contenido para aplicar.")
            return
        sobrescribir = QMessageBox.question(
            self, "Sobrescribir personalizados",
            "¿Quieres sobrescribir productos que ya tengan una descripción personalizada?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes

        n_mod = 0
        n_skip = 0
        for prodx in self.productos:
            if prodx.get("categoria") == categoria:
                sku = prodx.get("sku", "")
                d = self.descripciones.get(sku, {})
                campo_actual = d.get(campo, "").strip()
                if sobrescribir or not campo_actual:
                    d[campo] = value
                    self.descripciones[sku] = d
                    n_mod += 1
                else:
                    n_skip += 1
        guardar_descripciones(self.descripciones)
        QMessageBox.information(self, "Aplicado",
            f"{n_mod} productos de la categoría '{categoria}' modificados.\n{n_skip} productos no se modificaron por tener datos únicos.")
        self.cargar_para_sku(self.current_sku)

    def llenar_sku_combo(self):
        self.sku_combo.clear()
        for prod in self.productos:
            sku = prod.get("sku", "")
            nombre = prod.get("nombre", "")
            cat = prod.get("categoria", "")
            idwoo = str(prod.get("id", "-"))
            self.sku_combo.addItem(f"{sku} | {nombre} [{cat}]", userData=(sku, idwoo))
        self.sku_combo.addItem("Otro SKU...")

    def cargar_para_sku_combo(self):
        idx = self.sku_combo.currentIndex()
        if idx >= 0 and idx < self.sku_combo.count() - 1:
            sku, idwoo = self.sku_combo.itemData(idx)
        else:
            sku = self.sku_combo.currentText().split(" | ")[0].strip()
            idwoo = "-"
        self.current_sku = sku
        self.lbl_id.setText(f"ID Woo: {idwoo}")
        self.cargar_para_sku(sku)

    def cargar_para_sku(self, sku):
        data = self.descripciones.get(sku, {})
        self.desc_corta_edit.setPlainText(data.get("desc_corta", ""))
        self.desc_larga_edit.setPlainText(data.get("desc_larga", ""))
        self.categorias_edit.setText(data.get("categorias", ""))
        self.etiquetas_edit.setText(data.get("etiquetas", ""))
        self.clase_envio_edit.setText(data.get("clase_envio", ""))
        self.meta_table.setRowCount(0)
        for meta in data.get("meta_extra", []):
            row = self.meta_table.rowCount()
            self.meta_table.insertRow(row)
            self.meta_table.setItem(row, 0, QTableWidgetItem(meta.get("key", "")))
            self.meta_table.setItem(row, 1, QTableWidgetItem(meta.get("value", "")))
        self.actualizar_preview()

    def agregar_meta(self):
        row = self.meta_table.rowCount()
        self.meta_table.insertRow(row)
        self.meta_table.setItem(row, 0, QTableWidgetItem(""))
        self.meta_table.setItem(row, 1, QTableWidgetItem(""))

    def eliminar_meta(self):
        row = self.meta_table.currentRow()
        if row >= 0:
            self.meta_table.removeRow(row)

    def guardar(self):
        sku = self.sku_combo.currentText().split(" | ")[0].strip()
        if not sku:
            QMessageBox.warning(self, "Falta SKU", "Debes ingresar el SKU para guardar la descripción.")
            return
        data = {
            "desc_corta": self.desc_corta_edit.toPlainText().strip(),
            "desc_larga": self.desc_larga_edit.toPlainText().strip(),
            "categorias": self.categorias_edit.text().strip(),
            "etiquetas": self.etiquetas_edit.text().strip(),
            "clase_envio": self.clase_envio_edit.text().strip(),
            "meta_extra": [
                {"key": self.meta_table.item(r, 0).text(), "value": self.meta_table.item(r, 1).text()}
                for r in range(self.meta_table.rowCount())
                if self.meta_table.item(r, 0) and self.meta_table.item(r, 0).text().strip()
            ]
        }
        self.descripciones[sku] = data
        guardar_descripciones(self.descripciones)
        QMessageBox.information(self, "Guardado", "Descripción guardada correctamente.")

    def exportar_html(self):
        html = self.generar_html_export()
        fname, _ = QFileDialog.getSaveFileName(self, "Guardar HTML", f"{self.current_sku or 'descripcion'}.html", "Archivos HTML (*.html)")
        if fname:
            with open(fname, "w", encoding="utf-8") as f:
                f.write(html)
            QMessageBox.information(self, "Exportado", f"HTML exportado a {fname}")

    def generar_html_export(self):
        html = ""
        if self.desc_corta_edit.toPlainText().strip():
            html += f"<!-- DESCRIPCION_CORTA -->\n{self.desc_corta_edit.toPlainText().strip()}\n"
        if self.desc_larga_edit.toPlainText().strip():
            html += f"<!-- DESCRIPCION_LARGA -->\n{self.desc_larga_edit.toPlainText().strip()}\n"
        nota_compra = cargar_nota_compra_global()
        if nota_compra:
            html += f"<!-- NOTA_COMPRA -->\n{nota_compra}\n"
        return html

    def actualizar_preview(self):
        html = ""
        if self.desc_corta_edit.toPlainText().strip():
            html += f"<div style='font-size:12pt;color:#444;margin-bottom:10px;'><b>Corta:</b><br>{self.desc_corta_edit.toPlainText()}</div>"
        if self.desc_larga_edit.toPlainText().strip():
            html += f"<div style='font-size:12pt;color:#222;margin-bottom:10px;'><b>Larga:</b><br>{self.desc_larga_edit.toPlainText()}</div>"
        # Imágenes (del SKU)
        sku = self.current_sku or ""
        imagenes = obtener_imagenes_producto(sku)
        if imagenes:
            html += "<div style='margin:10px 0;'><b>Imágenes del producto:</b><br>"
            for imgfile in imagenes[:5]:  # máximo 5 imágenes
                html += f"<img src='file:///{imgfile}' style='max-width:120px;max-height:120px;margin:6px;border-radius:8px;border:1px solid #ccc;'/>\n"
            html += "</div>"
        # Nota de compra global
        nota_compra = cargar_nota_compra_global()
        if nota_compra:
            html += f"<div style='font-size:11pt;color:#388e3c;background:#e8ffe8;border-radius:5px;padding:7px;margin-top:12px;'><b>Nota de compra:</b><br>{nota_compra}</div>"
        self.preview_html.setHtml(html)