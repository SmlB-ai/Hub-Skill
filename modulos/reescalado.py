import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFileDialog, QSlider, QSpinBox, QComboBox, QProgressBar,
                            QMessageBox, QGridLayout, QFrame, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image
import time

class WorkerThread(QThread):
    """Hilo de trabajo para procesar imágenes sin bloquear la interfaz"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool)
    
    def __init__(self, input_dir, output_dir, width, height, mode="exact", format="PNG", quality=90):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.width = width
        self.height = height
        self.mode = mode
        self.format = format
        self.quality = quality
        self.running = True
        
    def run(self):
        try:
            # Encuentra todas las imágenes en el directorio de entrada
            image_files = []
            for root, _, files in os.walk(self.input_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                        image_files.append(os.path.join(root, file))
            
            total = len(image_files)
            if total == 0:
                self.finished.emit(False)
                return
                
            # Procesa cada imagen
            for i, image_path in enumerate(image_files):
                if not self.running:
                    break
                    
                try:
                    # Abre la imagen
                    img = Image.open(image_path)
                    
                    # Determina si se debe reescalar o mantener dimensiones originales
                    if self.width == 0 or self.height == 0:
                        # Si width o height es 0, mantener dimensiones originales
                        resized_img = img  # No hacer reescalado
                    else:
                        # Aplica el reescalado según el modo seleccionado
                        if self.mode == "exact":
                            resized_img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                        elif self.mode == "proporcional":
                            # Mantiene la proporción ajustando al ancho
                            ratio = self.width / img.width
                            new_height = int(img.height * ratio)
                            resized_img = img.resize((self.width, new_height), Image.Resampling.LANCZOS)
                        elif self.mode == "max":
                            # Escala manteniendo proporción pero sin exceder dimensiones máximas
                            img_ratio = img.width / img.height
                            target_ratio = self.width / self.height
                            if img_ratio > target_ratio:
                                # Limitar por ancho
                                new_width = self.width
                                new_height = int(new_width / img_ratio)
                            else:
                                # Limitar por alto
                                new_height = self.height
                                new_width = int(new_height * img_ratio)
                            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Crea el nombre de archivo de salida
                    filename = os.path.basename(image_path)
                    name, _ = os.path.splitext(filename)
                    output_format = self.format.lower()
                    
                    # Asegura que la extensión sea correcta
                    if output_format == "jpg":
                        output_format = "jpeg"
                    
                    output_path = os.path.join(self.output_dir, f"{name}.{output_format}")
                    
                    # Guarda la imagen con la calidad especificada
                    if output_format in ["jpeg", "jpg"]:
                        resized_img.save(output_path, format=output_format.upper(), quality=self.quality)
                    else:
                        resized_img.save(output_path, format=output_format.upper())
                        
                except Exception as e:
                    print(f"Error al procesar {image_path}: {e}")
                
                # Actualiza el progreso
                progress_value = int((i + 1) / total * 100)
                self.progress.emit(progress_value)
                
            self.finished.emit(True)
        except Exception as e:
            print(f"Error en el procesamiento: {e}")
            self.finished.emit(False)
    
    def stop(self):
        self.running = False


class ReescaladoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reescalado de Imágenes")
        self.setMinimumSize(900, 700)  # Ventana más grande
        self.input_dir = ""
        self.output_dir = ""
        self.worker = None
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Reescalado de Imágenes")
        title_label.setStyleSheet("""
            font-size: 22pt; 
            font-weight: bold; 
            margin-bottom: 20px;
            color: #2196F3;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Marco para la visualización de imágenes
        self.preview_frame = QFrame()
        self.preview_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.preview_frame.setMinimumHeight(300)  # Vista previa más grande
        self.preview_frame.setStyleSheet("""
            QFrame {
                background-color: #2C2C2C;
                border-radius: 10px;
                border: 2px solid #3C3C3C;
            }
        """)
        
        preview_layout = QVBoxLayout()
        self.image_preview = QLabel("Vista previa no disponible")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setStyleSheet("""
            color: #FFFFFF;
            background-color: transparent;
            padding: 10px;
        """)
        preview_layout.addWidget(self.image_preview)
        self.preview_frame.setLayout(preview_layout)
        
        main_layout.addWidget(self.preview_frame)
        
        # Selección de directorios
        dir_layout = QGridLayout()
        
        # Directorio de entrada
        input_label = QLabel("Directorio de entrada:")
        input_label.setStyleSheet("color: #FFFFFF;")
        dir_layout.addWidget(input_label, 0, 0)
        
        self.input_path_label = QLabel("No seleccionado")
        self.input_path_label.setStyleSheet("""
            background-color: #424242;
            padding: 8px;
            border-radius: 5px;
            color: #FFFFFF;
        """)
        dir_layout.addWidget(self.input_path_label, 0, 1)
        
        input_btn = QPushButton("Seleccionar")
        input_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        input_btn.clicked.connect(self.select_input_dir)
        dir_layout.addWidget(input_btn, 0, 2)
        
        # Directorio de salida
        output_label = QLabel("Directorio de salida:")
        output_label.setStyleSheet("color: #FFFFFF;")
        dir_layout.addWidget(output_label, 1, 0)
        
        self.output_path_label = QLabel("No seleccionado")
        self.output_path_label.setStyleSheet("""
            background-color: #424242;
            padding: 8px;
            border-radius: 5px;
            color: #FFFFFF;
        """)
        dir_layout.addWidget(self.output_path_label, 1, 1)
        
        output_btn = QPushButton("Seleccionar")
        output_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        output_btn.clicked.connect(self.select_output_dir)
        dir_layout.addWidget(output_btn, 1, 2)
        
        main_layout.addLayout(dir_layout)
        
        # Opciones de reescalado
        options_layout = QGridLayout()
        
        # Checkbox para mantener dimensiones originales
        self.keep_dimensions_check = QCheckBox("Mantener dimensiones originales")
        self.keep_dimensions_check.setStyleSheet("color: #FFFFFF;")
        self.keep_dimensions_check.toggled.connect(self.toggle_dimension_fields)
        options_layout.addWidget(self.keep_dimensions_check, 0, 0, 1, 4)
        
        # Dimensiones
        width_label = QLabel("Ancho:")
        width_label.setStyleSheet("color: #FFFFFF;")
        options_layout.addWidget(width_label, 1, 0)
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(800)
        self.width_spin.setMinimumWidth(220)  # Más ancho
        self.width_spin.setStyleSheet("""
            QSpinBox {
                background-color: #424242;
                color: #FFFFFF;
                border: 1px solid #555555;
                padding: 3px;
                border-radius: 5px;
            }
        """)
        options_layout.addWidget(self.width_spin, 1, 1)
        
        height_label = QLabel("Alto:")
        height_label.setStyleSheet("color: #FFFFFF;")
        options_layout.addWidget(height_label, 1, 2)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(600)
        self.height_spin.setMinimumWidth(220)  # Más ancho
        self.height_spin.setStyleSheet("""
            QSpinBox {
                background-color: #424242;
                color: #FFFFFF;
                border: 1px solid #555555;
                padding: 3px;
                border-radius: 5px;
            }
        """)
        options_layout.addWidget(self.height_spin, 1, 3)
        
        # Modo de reescalado
        mode_label = QLabel("Modo de reescalado:")
        mode_label.setStyleSheet("color: #FFFFFF;")
        options_layout.addWidget(mode_label, 2, 0)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Exacto", "Proporcional", "Máximo"])
        self.mode_combo.setStyleSheet("""
            QComboBox {
                background-color: #424242;
                color: #FFFFFF;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid #FFFFFF;
                border-right: 5px solid transparent;
                border-top: 5px solid #FFFFFF;
            }
        """)
        options_layout.addWidget(self.mode_combo, 2, 1)
        
        # Formato de salida
        format_label = QLabel("Formato de salida:")
        format_label.setStyleSheet("color: #FFFFFF;")
        options_layout.addWidget(format_label, 2, 2)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPG", "WEBP"])
        self.format_combo.setStyleSheet("""
            QComboBox {
                background-color: #424242;
                color: #FFFFFF;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid #FFFFFF;
                border-right: 5px solid transparent;
                border-top: 5px solid #FFFFFF;
            }
        """)
        self.format_combo.currentTextChanged.connect(self.toggle_quality_option)
        options_layout.addWidget(self.format_combo, 2, 3)
        
        # Calidad (solo para JPG)
        quality_label = QLabel("Calidad:")
        quality_label.setStyleSheet("color: #FFFFFF;")
        options_layout.addWidget(quality_label, 3, 0)
        
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(90)
        self.quality_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #565656;
                height: 10px;
                background: #2C2C2C;
                margin: 0px;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                border: none;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
        options_layout.addWidget(self.quality_slider, 3, 1)
        
        self.quality_value = QLabel("90%")
        self.quality_value.setStyleSheet("color: #FFFFFF;")
        self.quality_slider.valueChanged.connect(lambda v: self.quality_value.setText(f"{v}%"))
        options_layout.addWidget(self.quality_value, 3, 2)
        
        main_layout.addLayout(options_layout)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 5px;
                text-align: center;
                background-color: #2C2C2C;
                color: #FFFFFF;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Iniciar Procesamiento")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:disabled {
                background-color: #777777;
            }
        """)
        self.start_button.clicked.connect(self.start_processing)
        button_layout.addWidget(self.start_button)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:disabled {
                background-color: #777777;
            }
        """)
        self.cancel_button.clicked.connect(self.cancel_processing)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # Establecer el estilo general de la ventana
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
            }
        """)
        
        self.setLayout(main_layout)
    
    def toggle_dimension_fields(self):
        """Habilita/deshabilita los campos de dimensiones según el estado del checkbox"""
        enabled = not self.keep_dimensions_check.isChecked()
        self.width_spin.setEnabled(enabled)
        self.height_spin.setEnabled(enabled)
        self.mode_combo.setEnabled(enabled)
    
    def toggle_quality_option(self, format_text):
        """Habilita o deshabilita las opciones de calidad según el formato seleccionado"""
        is_jpg = format_text == "JPG"
        self.quality_slider.setEnabled(is_jpg)
        self.quality_value.setEnabled(is_jpg)
        if not is_jpg:
            self.quality_value.setStyleSheet("color: #777777;")
        else:
            self.quality_value.setStyleSheet("color: #FFFFFF;")
    
    def select_input_dir(self):
        """Selecciona el directorio de entrada"""
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio de Entrada")
        if directory:
            self.input_dir = directory
            self.input_path_label.setText(directory)
            # Buscar una imagen para la vista previa
            self.load_preview_image()
    
    def select_output_dir(self):
        """Selecciona el directorio de salida"""
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio de Salida")
        if directory:
            self.output_dir = directory
            self.output_path_label.setText(directory)
    
    def load_preview_image(self):
        """Carga una imagen para la vista previa"""
        if not self.input_dir:
            return
            
        # Busca la primera imagen en el directorio
        for root, _, files in os.walk(self.input_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
                    image_path = os.path.join(root, file)
                    # Carga la imagen en la vista previa
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        # Escala la imagen para que quepa en el área de vista previa
                        scaled_pixmap = pixmap.scaled(
                            self.preview_frame.width() - 40, 
                            self.preview_frame.height() - 40,
                            Qt.AspectRatioMode.KeepAspectRatio, 
                            Qt.TransformationMode.SmoothTransformation
                        )
                        self.image_preview.setPixmap(scaled_pixmap)
                        return
    
    def get_resize_mode(self):
        """Convierte el texto del combobox al modo de reescalado para el worker"""
        mode_text = self.mode_combo.currentText()
        if mode_text == "Exacto":
            return "exact"
        elif mode_text == "Proporcional":
            return "proporcional"
        else:  # "Máximo"
            return "max"
    
    def start_processing(self):
        """Inicia el procesamiento de imágenes"""
        if not self.input_dir or not self.output_dir:
            QMessageBox.warning(self, "Advertencia", "Debes seleccionar los directorios de entrada y salida.")
            return
        
        # Crea y configura el trabajador
        self.worker = WorkerThread(
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            width=0 if self.keep_dimensions_check.isChecked() else self.width_spin.value(),
            height=0 if self.keep_dimensions_check.isChecked() else self.height_spin.value(),
            mode=self.get_resize_mode(),
            format=self.format_combo.currentText(),
            quality=self.quality_slider.value()
        )
        
        # Conecta las señales
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.processing_finished)
        
        # Actualiza la interfaz
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)
        
        # Inicia el trabajador
        self.worker.start()
    
    def cancel_processing(self):
        """Cancela el procesamiento de imágenes"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.progress_bar.setValue(0)
            self.start_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
    
    def update_progress(self, value):
        """Actualiza la barra de progreso"""
        self.progress_bar.setValue(value)
    
    def processing_finished(self, success):
        """Maneja el fin del procesamiento"""
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        
        if success:
            QMessageBox.information(self, "Éxito", "Procesamiento de imágenes completado con éxito.")
        else:
            QMessageBox.warning(self, "Advertencia", "Ocurrió un error durante el procesamiento. Verifica los directorios y vuelve a intentar.")