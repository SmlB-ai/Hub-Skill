import os
import json
import shutil
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QListWidget, QListWidgetItem, QComboBox, QMessageBox, QSpinBox, QSlider,
    QCheckBox, QGroupBox, QAbstractItemView
)
from PyQt6.QtGui import QPixmap, QIcon, QDragEnterEvent, QDropEvent
from PyQt6.QtCore import Qt, QSize
from PIL import Image
from PyQt6.QtCore import pyqtSignal

DATA_DIR = "datos"
PRODUCTOS_FILE = os.path.join(DATA_DIR, "productos.json")
DEFAULT_IMAGES_ROOT = os.path.abspath("imagenes_productos")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

class ReescaladoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión y Optimización de Imágenes de Productos")
        self.setMinimumSize(950, 600)
        self.setAcceptDrops(True)
        self.imagenes_raiz = self.cargar_ruta_raiz()
        self.carpeta_actual = ""
        self.productos = []
        self.imagenes = []
        self.sku_seleccionado = ""
        self.formato_salida = "JPG"
        self.guardar_original = False
        self.init_ui()
        self.cargar_productos()
        self.actualizar_lista_imagenes()

    def cargar_ruta_raiz(self):
        config_file = os.path.join(DATA_DIR, "imagenes_config.json")
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("imagenes_raiz", DEFAULT_IMAGES_ROOT)
        return DEFAULT_IMAGES_ROOT

    def guardar_ruta_raiz(self):
        config_file = os.path.join(DATA_DIR, "imagenes_config.json")
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump({"imagenes_raiz": self.imagenes_raiz}, f, ensure_ascii=False, indent=2)

    def init_ui(self):
        main = QHBoxLayout(self)
        # Lado izquierdo: Producto y lista de imágenes
        left = QVBoxLayout()
        # Producto
        g_prod = QGroupBox("Producto")
        prod_layout = QHBoxLayout()
        self.producto_combo = QComboBox()
        self.producto_combo.currentIndexChanged.connect(self.cambiar_producto)
        prod_layout.addWidget(self.producto_combo)
        # --- BOTÓN REFRESCAR PRODUCTOS ---
        self.btn_refresh_productos = QPushButton("Refrescar productos")
        self.btn_refresh_productos.setToolTip("Volver a cargar la lista de productos")
        self.btn_refresh_productos.clicked.connect(self.cargar_productos)
        prod_layout.addWidget(self.btn_refresh_productos)
        # ---------------------------------
        g_prod.setLayout(prod_layout)
        left.addWidget(g_prod)

        # Lista de imágenes con drag y visual principal
        g_imgs = QGroupBox("Imágenes asociadas")
        img_layout = QVBoxLayout()
        self.lista_imagenes = QListWidget()
        self.lista_imagenes.setIconSize(QSize(80, 80))
        self.lista_imagenes.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.lista_imagenes.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.lista_imagenes.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.lista_imagenes.itemClicked.connect(self.mostrar_vista_previa)
        img_layout.addWidget(self.lista_imagenes)
        btns = QHBoxLayout()
        self.btn_borrar = QPushButton("Eliminar")
        self.btn_borrar.setToolTip("Eliminar imagen seleccionada")
        self.btn_borrar.setFixedWidth(90)
        self.btn_borrar.clicked.connect(self.eliminar_imagen_seleccionada)
        btns.addWidget(self.btn_borrar)
        self.btn_principal = QPushButton("Marcar principal")
        self.btn_principal.setToolTip("Marcar imagen seleccionada como principal")
        self.btn_principal.setFixedWidth(110)
        self.btn_principal.clicked.connect(self.marcar_imagen_principal)
        btns.addWidget(self.btn_principal)
        img_layout.addLayout(btns)
        g_imgs.setLayout(img_layout)
        left.addWidget(g_imgs)

        # Botón agregar imágenes
        btns2 = QHBoxLayout()
        btn_agregar = QPushButton("Agregar imágenes (+)")
        btn_agregar.clicked.connect(self.abrir_archivos)
        btns2.addWidget(btn_agregar)
        left.addLayout(btns2)
        main.addLayout(left,2)

        # Lado derecho: Vista previa + opciones
        right = QVBoxLayout()
        # Vista previa
        self.preview_label = QLabel("Arrastra imágenes aquí o usa el botón '+'.")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(320, 240)
        self.preview_label.setStyleSheet("background: #222; border: 2px dashed #2196F3; color: #aaa; margin-bottom:8px;")
        right.addWidget(self.preview_label)

        # Opciones
        g_opts = QGroupBox("Opciones de guardado")
        opts = QVBoxLayout()
        # Resolución
        res_layout = QHBoxLayout()
        self.chk_original = QCheckBox("Mantener resolución original")
        self.chk_original.toggled.connect(self.toggle_res_inputs)
        res_layout.addWidget(self.chk_original)
        res_layout.addWidget(QLabel("Ancho:"))
        self.ancho_spin = QSpinBox()
        self.ancho_spin.setRange(64, 5000)
        self.ancho_spin.setValue(900)
        res_layout.addWidget(self.ancho_spin)
        res_layout.addWidget(QLabel("Alto:"))
        self.alto_spin = QSpinBox()
        self.alto_spin.setRange(64, 5000)
        self.alto_spin.setValue(900)
        res_layout.addWidget(self.alto_spin)
        opts.addLayout(res_layout)
        # Formato/calidad
        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(QLabel("Formato salida:"))
        self.formato_combo = QComboBox()
        self.formato_combo.addItems(["JPG", "PNG", "WEBP"])
        self.formato_combo.currentTextChanged.connect(self.cambiar_formato_salida)
        fmt_layout.addWidget(self.formato_combo)
        fmt_layout.addWidget(QLabel("Calidad JPG/WEBP:"))
        self.calidad_slider = QSlider(Qt.Orientation.Horizontal)
        self.calidad_slider.setRange(10, 100)
        self.calidad_slider.setValue(88)
        self.calidad_slider.setFixedWidth(100)
        fmt_layout.addWidget(self.calidad_slider)
        opts.addLayout(fmt_layout)
        g_opts.setLayout(opts)
        right.addWidget(g_opts)

        # Acciones
        act = QHBoxLayout()
        btn_guardar = QPushButton("Optimizar y Guardar")
        btn_guardar.clicked.connect(self.optimizar_y_guardar)
        act.addWidget(btn_guardar)
        act.addStretch()
        btn_root = QPushButton("Cambiar directorio imágenes")
        btn_root.clicked.connect(self.cambiar_directorio_raiz)
        act.addWidget(btn_root)
        right.addLayout(act)

        main.addLayout(right,3)

    # DRAG & DROP
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        self.cargar_imagenes(files)
    def abrir_archivos(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Selecciona imágenes", "", "Imágenes (*.png *.jpg *.jpeg *.webp *.bmp *.gif)")
        if files:
            self.cargar_imagenes(files)
    def cargar_imagenes(self, files):
        for f in files:
            if not os.path.isfile(f):
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext not in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"]:
                continue
            if f not in self.imagenes:
                self.imagenes.append(f)
        self.actualizar_lista_imagenes()

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
            ensure_dir(self.carpeta_actual)

    def cambiar_producto(self, idx):
        if idx < 0 or idx >= len(self.productos):
            return
        self.sku_seleccionado = self.productos[idx].get("sku", "")
        self.carpeta_actual = os.path.join(self.imagenes_raiz, self.sku_seleccionado)
        ensure_dir(self.carpeta_actual)
        self.imagenes = []
        for f in os.listdir(self.carpeta_actual):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif')):
                self.imagenes.append(os.path.join(self.carpeta_actual, f))
        self.actualizar_lista_imagenes()

    def actualizar_lista_imagenes(self):
        self.lista_imagenes.clear()
        for i, img_path in enumerate(self.imagenes):
            try:
                pixmap = QPixmap(img_path).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                name = os.path.basename(img_path)
                if i == 0:
                    item = QListWidgetItem(QIcon(pixmap), f"★ {name} (principal)")
                    item.setBackground(Qt.GlobalColor.yellow)
                else:
                    item = QListWidgetItem(QIcon(pixmap), name)
                # Guarda la ruta real en el item para obtenerla en el orden visual luego
                item.setData(Qt.ItemDataRole.UserRole, img_path)
                self.lista_imagenes.addItem(item)
            except Exception:
                item = QListWidgetItem(os.path.basename(img_path))
                item.setData(Qt.ItemDataRole.UserRole, img_path)
                self.lista_imagenes.addItem(item)

    def mostrar_vista_previa(self, item):
        idx = self.lista_imagenes.row(item)
        if idx < 0 or idx >= len(self.imagenes):
            self.preview_label.setText("Vista previa no disponible")
            return
        img_path = item.data(Qt.ItemDataRole.UserRole)
        pixmap = QPixmap(img_path).scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.preview_label.setPixmap(pixmap)

    def eliminar_imagen_seleccionada(self):
        idx = self.lista_imagenes.currentRow()
        if idx < 0 or idx >= self.lista_imagenes.count():
            return
        item = self.lista_imagenes.item(idx)
        img_path = item.data(Qt.ItemDataRole.UserRole)
        # Elimina de self.imagenes también
        if img_path in self.imagenes:
            self.imagenes.remove(img_path)
        if os.path.isfile(img_path):
            try:
                os.remove(img_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo eliminar la imagen: {e}")
        self.actualizar_lista_imagenes()
        if self.carpeta_actual and os.path.exists(self.carpeta_actual):
            if not any(os.scandir(self.carpeta_actual)):
                try:
                    shutil.rmtree(self.carpeta_actual)
                except Exception:
                    pass

    def marcar_imagen_principal(self):
        idx = self.lista_imagenes.currentRow()
        if idx < 0 or idx >= self.lista_imagenes.count():
            return
        # Reordena visualmente el QListWidget
        item = self.lista_imagenes.takeItem(idx)
        self.lista_imagenes.insertItem(0, item)
        self.lista_imagenes.setCurrentRow(0)
        # Opcional: reordena self.imagenes para mantener sincronía
        img_path = item.data(Qt.ItemDataRole.UserRole)
        if img_path in self.imagenes:
            self.imagenes.remove(img_path)
            self.imagenes.insert(0, img_path)
        self.actualizar_lista_imagenes()

    def cambiar_formato_salida(self, texto):
        self.formato_salida = texto.upper()

    def toggle_res_inputs(self, checked):
        self.ancho_spin.setEnabled(not checked)
        self.alto_spin.setEnabled(not checked)
        self.guardar_original = checked

    def optimizar_y_guardar(self):
        if not self.sku_seleccionado or not self.carpeta_actual:
            QMessageBox.warning(self, "Error", "Debes seleccionar un producto.")
            return
        ancho = self.ancho_spin.value()
        alto = self.alto_spin.value()
        calidad = self.calidad_slider.value()
        formato = self.formato_salida.lower()
        nuevas_imagenes = []
        # Limpia carpeta destino antes de guardar (excepto metadatos)
        for f in os.listdir(self.carpeta_actual):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif')):
                try:
                    os.remove(os.path.join(self.carpeta_actual, f))
                except Exception:
                    pass
        # Usa el orden visual del QListWidget:
        for i in range(self.lista_imagenes.count()):
            item = self.lista_imagenes.item(i)
            img_src = item.data(Qt.ItemDataRole.UserRole)
            ext = "." + formato
            if i == 0:
                nombre_destino = f"{self.sku_seleccionado}_main{ext}"
            else:
                nombre_destino = f"{self.sku_seleccionado}_{i:02d}{ext}"
            dest_path = os.path.join(self.carpeta_actual, nombre_destino)
            try:
                img = Image.open(img_src)
                img = img.convert("RGB")
                if not self.guardar_original:
                    img = img.resize((ancho, alto), Image.Resampling.LANCZOS)
                # Guardar en formato elegido
                if formato in ["jpg", "jpeg"]:
                    img.save(dest_path, quality=calidad)
                elif formato == "webp":
                    img.save(dest_path, quality=calidad, format="WEBP")
                else:
                    img.save(dest_path)
                nuevas_imagenes.append(dest_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo procesar {img_src}: {e}")
        # Sincroniza self.imagenes al nuevo orden y rutas
        self.imagenes = nuevas_imagenes
        self.guardar_metadatos(formato)
        self.actualizar_lista_imagenes()
        QMessageBox.information(self, "Listo", "Imágenes optimizadas y guardadas.")

    def guardar_metadatos(self, formato):
        if not self.carpeta_actual:
            return
        if not os.path.exists(self.carpeta_actual):
            return
        imgs = sorted([f for f in os.listdir(self.carpeta_actual) if f.lower().endswith(f'.{formato}')])
        main_img = next((f for f in imgs if "_main" in f), imgs[0] if imgs else "")
        meta = {
            "imagenes": imgs,
            "principal": main_img
        }
        with open(os.path.join(self.carpeta_actual, "imagenes.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    def cambiar_directorio_raiz(self):
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar directorio raíz de imágenes")
        if directory:
            self.imagenes_raiz = directory
            self.carpeta_actual = os.path.join(self.imagenes_raiz, self.sku_seleccionado)
            self.guardar_ruta_raiz()
            self.actualizar_lista_imagenes()