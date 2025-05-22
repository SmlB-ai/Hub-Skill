import os
import shutil
import json
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog, QDialog,
    QVBoxLayout, QDialogButtonBox, QSlider, QSpinBox, QFormLayout
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize

CONFIG_FILE = "config.json"
DEFAULT_LOGO = os.path.abspath(os.path.join("recursos", "logo.png"))

def guardar_config_logo(ruta_logo, logo_size):
    data = {"logo": ruta_logo, "logo_size": logo_size}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cargar_config_logo():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                logo = data.get("logo", DEFAULT_LOGO)
                size = data.get("logo_size", 100)
                return logo, size
            except Exception:
                return DEFAULT_LOGO, 100
    return DEFAULT_LOGO, 100

class LogoConfigDialog(QDialog):
    def __init__(self, parent, current_logo_path, current_size):
        super().__init__(parent)
        self.setWindowTitle("Configurar Logo")
        self.setModal(True)
        self.setFixedSize(350, 410)

        self.logo_path = current_logo_path
        self.logo_size = current_size

        layout = QVBoxLayout(self)
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setFixedSize(200, 200)
        layout.addWidget(self.logo_label)

        self.actualizar_logo()

        # Cambiar logo
        btn_cambiar = QPushButton("Cambiar Logo…")
        btn_cambiar.setIcon(QIcon.fromTheme("document-open"))
        btn_cambiar.clicked.connect(self.cambiar_logo)
        layout.addWidget(btn_cambiar, alignment=Qt.AlignmentFlag.AlignCenter)

        # Cambiar tamaño
        form = QFormLayout()
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(64)
        self.size_slider.setMaximum(256)
        self.size_slider.setValue(self.logo_size)
        self.size_slider.setTickInterval(4)
        self.size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.size_spin = QSpinBox()
        self.size_spin.setRange(64, 256)
        self.size_spin.setValue(self.logo_size)
        self.size_spin.setSuffix(" px")
        self.size_slider.valueChanged.connect(self.size_spin.setValue)
        self.size_spin.valueChanged.connect(self.size_slider.setValue)
        self.size_slider.valueChanged.connect(self.update_size_from_slider)
        hbox = QHBoxLayout()
        hbox.addWidget(self.size_slider)
        hbox.addWidget(self.size_spin)
        form.addRow("Tamaño logo:", hbox)
        layout.addLayout(form)

        self.btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)
        layout.addWidget(self.btn_box)

    def actualizar_logo(self):
        if os.path.exists(self.logo_path):
            pixmap = QPixmap(self.logo_path).scaled(
                self.logo_size, self.logo_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.clear()

    def cambiar_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecciona una imagen de logo", "", "Imágenes (*.png *.jpg *.jpeg *.webp *.ico)")
        if path:
            ext = os.path.splitext(path)[1].lower()
            if ext not in [".png", ".jpg", ".jpeg", ".webp", ".ico"]:
                return
            nueva_ruta = os.path.abspath(os.path.join("recursos", "logo_personalizado" + ext))
            shutil.copy(path, nueva_ruta)
            self.logo_path = nueva_ruta
            self.actualizar_logo()

    def update_size_from_slider(self, value):
        self.logo_size = value
        self.actualizar_logo()

    def get_logo(self):
        return self.logo_path, self.logo_size

class LogoPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.logo_path, self.logo_size = cargar_config_logo()
        self.setMinimumHeight(self.logo_size + 14)

        # Layout absoluto para poner botón sobre logo
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self.logo_frame = QWidget()
        self.logo_frame.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.logo_frame.setMinimumSize(self.logo_size, self.logo_size)
        self.logo_frame.setMaximumSize(300, 300)

        self.logo_label = QLabel(self.logo_frame)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setFixedSize(self.logo_size, self.logo_size)
        self.logo_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # Sin fondo
        self.logo_label.setStyleSheet("background: transparent; border: none;")

        # Botón engranaje en la esquina inferior derecha, dentro del logo
        self.btn_config = QPushButton(self.logo_frame)
        engranaje_icon = QIcon.fromTheme("settings", QIcon("recursos/engranaje.png"))
        self.btn_config.setIcon(engranaje_icon)
        self.btn_config.setIconSize(QSize(18, 18))  # ¡MÁS PEQUEÑO!
        self.btn_config.setFixedSize(22, 22)        # ¡MÁS PEQUEÑO!
        self.btn_config.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_config.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                padding: 0;
            }
            QPushButton:hover {
                background: #ececec;
                border-radius: 11px;
            }
        """)
        self.btn_config.clicked.connect(self.abrir_config)

        self._main_layout.addWidget(self.logo_frame, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.actualizar_logo()
        self.position_config_button()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_config_button()

    def position_config_button(self):
        """Coloca el engranaje en la esquina inferior derecha interna del logo."""
        margin = 4
        size = self.logo_size
        btn_size = self.btn_config.width()
        self.logo_label.setFixedSize(size, size)
        self.btn_config.move(size - btn_size - margin, size - btn_size - margin)
        self.logo_frame.setFixedSize(size, size)

    def actualizar_logo(self):
        if os.path.exists(self.logo_path):
            pixmap = QPixmap(self.logo_path).scaled(
                self.logo_size, self.logo_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        else:
            self.logo_label.clear()
        self.position_config_button()

    def abrir_config(self):
        dlg = LogoConfigDialog(self, self.logo_path, self.logo_size)
        if dlg.exec():
            self.logo_path, self.logo_size = dlg.get_logo()
            guardar_config_logo(self.logo_path, self.logo_size)
            self.actualizar_logo()
            mw = self.parentWidget()
            if mw:
                win = mw.window()
                win.setWindowIcon(QIcon(self.logo_path))