from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QHBoxLayout, QFileDialog, QFrame, QComboBox, QColorDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer
import os
import random

# Importar la función para obtener productos
from modulos.productos import obtener_productos

class QrGeneratorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Códigos QR")
        self.setMinimumSize(700, 600)
        self.qr_code = None
        self.qr_color = "#000000"
        self.bg_color = "#FFFFFF"

        # Obtener productos
        self.productos = obtener_productos()

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Título
        title_label = QLabel("Generador de Códigos QR")
        title_label.setStyleSheet("font-size: 24pt; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Selector de producto
        producto_layout = QHBoxLayout()
        producto_label = QLabel("Seleccionar producto:")
        producto_label.setStyleSheet("font-size: 14pt;")
        producto_layout.addWidget(producto_label)

        self.producto_combo = QComboBox()
        self.producto_combo.addItem("Sin producto")
        for prod in self.productos:
            self.producto_combo.addItem(prod['nombre'])
        self.producto_combo.currentIndexChanged.connect(self.on_producto_selected)
        self.producto_combo.setStyleSheet("font-size: 12pt; padding: 8px;")
        producto_layout.addWidget(self.producto_combo)
        main_layout.addLayout(producto_layout)

        # Área del formulario para texto/URL manual
        form_layout = QVBoxLayout()
        input_label = QLabel("Texto o URL:")
        input_label.setStyleSheet("font-size: 14pt;")
        form_layout.addWidget(input_label)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Ingrese texto o URL para el código QR")
        self.text_input.setStyleSheet("font-size: 12pt; padding: 8px;")
        form_layout.addWidget(self.text_input)

        # Selección de estilo
        style_layout = QHBoxLayout()
        style_label = QLabel("Estilo:")
        style_label.setStyleSheet("font-size: 14pt;")
        style_layout.addWidget(style_label)

        self.style_combo = QComboBox()
        self.style_combo.addItems(["Cuadrado", "Redondeado", "Circular"])
        self.style_combo.setStyleSheet("font-size: 12pt; padding: 8px;")
        style_layout.addWidget(self.style_combo)
        form_layout.addLayout(style_layout)

        # Selección de colores
        colors_layout = QHBoxLayout()
        qr_color_button = QPushButton("Color del QR")
        qr_color_button.setStyleSheet("font-size: 12pt; padding: 8px;")
        qr_color_button.clicked.connect(self.select_qr_color)
        colors_layout.addWidget(qr_color_button)

        bg_color_button = QPushButton("Color de Fondo")
        bg_color_button.setStyleSheet("font-size: 12pt; padding: 8px;")
        bg_color_button.clicked.connect(self.select_bg_color)
        colors_layout.addWidget(bg_color_button)
        form_layout.addLayout(colors_layout)

        main_layout.addLayout(form_layout)

        # Área de visualización del QR
        self.preview_frame = QFrame()
        self.preview_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.preview_frame.setMinimumHeight(300)
        self.preview_frame.setStyleSheet("background-color: #424242; border-radius: 10px;")
        preview_layout = QVBoxLayout()
        self.qr_preview = QLabel("Vista previa del código QR")
        self.qr_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_preview.setStyleSheet("font-size: 14pt; color: #888;")
        preview_layout.addWidget(self.qr_preview)
        self.preview_frame.setLayout(preview_layout)
        main_layout.addWidget(self.preview_frame)

        # Botones de acción
        button_layout = QHBoxLayout()
        generate_button = QPushButton("Generar QR")
        generate_button.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            font-size: 14pt;
            padding: 10px;
            border-radius: 8px;
        """)
        generate_button.clicked.connect(self.generate_qr)
        button_layout.addWidget(generate_button)

        save_button = QPushButton("Guardar QR")
        save_button.setStyleSheet("""
            background-color: #2196F3;
            color: white;
            font-size: 14pt;
            padding: 10px;
            border-radius: 8px;
        """)
        save_button.clicked.connect(self.save_qr)
        button_layout.addWidget(save_button)

        random_button = QPushButton("QR Aleatorio")
        random_button.setStyleSheet("""
            background-color: #9C27B0;
            color: white;
            font-size: 14pt;
            padding: 10px;
            border-radius: 8px;
        """)
        random_button.clicked.connect(self.random_qr)
        button_layout.addWidget(random_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def on_producto_selected(self, idx):
        if idx <= 0:
            self.text_input.setText("")
        else:
            producto = self.productos[idx - 1]
            # Puedes elegir qué información poner en el QR
            if 'url' in producto:
                self.text_input.setText(producto['url'])
            else:
                self.text_input.setText(f"Producto: {producto['nombre']} (ID: {producto['id']})")

    def generate_qr(self):
        text = self.text_input.text()
        if not text:
            self.qr_preview.setText("Por favor, ingrese texto o URL")
            return
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)

            style = self.style_combo.currentText()
            if style == "Redondeado":
                module_drawer = RoundedModuleDrawer()
            elif style == "Circular":
                module_drawer = CircleModuleDrawer()
            else:
                module_drawer = None

            qr_color_rgb = tuple(int(self.qr_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            bg_color_rgb = tuple(int(self.bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

            if module_drawer:
                img = qr.make_image(
                    image_factory=StyledPilImage,
                    module_drawer=module_drawer,
                    color=qr_color_rgb,
                    background=bg_color_rgb
                )
            else:
                img = qr.make_image(
                    fill_color=self.qr_color,
                    back_color=self.bg_color
                )

            temp_path = os.path.join(os.path.dirname(__file__), "temp_qr.png")
            img.save(temp_path)

            pixmap = QPixmap(temp_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.preview_frame.width() - 40,
                    self.preview_frame.height() - 40,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.qr_preview.setPixmap(scaled_pixmap)
                self.qr_code = img
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            self.qr_preview.setText(f"Error al generar QR: {str(e)}")

    def save_qr(self):
        if not self.qr_code:
            self.qr_preview.setText("Primero genere un código QR")
            return
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Guardar Código QR", "", "PNG (*.png);;JPEG (*.jpg *.jpeg);;All Files (*)"
            )
            if file_path:
                self.qr_code.save(file_path)
        except Exception as e:
            self.qr_preview.setText(f"Error al guardar: {str(e)}")

    def select_qr_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.qr_color = color.name()

    def select_bg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.bg_color = color.name()

    def random_qr(self):
        random_texts = [
            "https://www.example.com",
            "¡Escanea este código para una sorpresa!",
            "Aplicación Modular - Generador QR",
            "PyQt6 es genial para interfaces",
            "Código aleatorio: " + str(random.randint(10000, 99999))
        ]
        self.text_input.setText(random.choice(random_texts))
        self.qr_color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        self.bg_color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        self.style_combo.setCurrentIndex(random.randint(0, 2))
        self.generate_qr()