import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QWidget, QMessageBox,
                            QScrollArea, QSpinBox, QGroupBox, QSlider, QCheckBox,
                            QProgressBar, QListWidget, QSplitter, QTabWidget)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QSize, QRect, QPoint, pyqtSignal, QThread
from PIL import Image, ImageQt, ImageEnhance, ImageFilter, ImageOps
import cairosvg
import io
import threading

class ImageProcessor(QThread):
    """Clase para procesar imágenes en segundo plano"""
    progress_updated = pyqtSignal(int)
    processing_complete = pyqtSignal(list)
    
    def __init__(self, base_image, design_files, target_area, apply_effects, output_folder):
        super().__init__()
        self.base_image = base_image
        self.design_files = design_files
        self.target_area = target_area  # (x, y, width, height)
        self.apply_effects = apply_effects
        self.output_folder = output_folder
        
    def run(self):
        results = []
        
        for i, design_path in enumerate(self.design_files):
            try:
                # Cargar el diseño
                design_image = self.load_image_file(design_path)
                if design_image is None:
                    continue
                
                # Asegurarse que tiene transparencia
                if design_image.mode != 'RGBA':
                    design_image = design_image.convert('RGBA')
                
                # Redimensionar el diseño para ajustarse al área objetivo
                design_image = self.resize_to_fit(design_image, 
                                                self.target_area[2], 
                                                self.target_area[3])
                
                # Crear una copia de la imagen base
                result = self.base_image.copy()
                if result.mode != 'RGBA':
                    result = result.convert('RGBA')
                
                # Posicionar el diseño en el área objetivo
                if self.apply_effects:
                    result = self.apply_realistic_effects(result, design_image, 
                                                        self.target_area[0], 
                                                        self.target_area[1])
                else:
                    # Pegar el diseño normalmente
                    result.paste(design_image, 
                              (self.target_area[0], self.target_area[1]), 
                              design_image)
                
                # Guardar resultado
                output_filename = os.path.join(
                    self.output_folder, 
                    f"mockup_{os.path.splitext(os.path.basename(design_path))[0]}.png"
                )
                result.save(output_filename, format='PNG')
                
                results.append((output_filename, result))
            except Exception as e:
                print(f"Error procesando {design_path}: {e}")
            
            # Actualizar progreso
            progress = int((i + 1) / len(self.design_files) * 100)
            self.progress_updated.emit(progress)
        
        self.processing_complete.emit(results)
    
    def load_image_file(self, file_path):
        """Cargar una imagen desde varias extensiones posibles"""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            # Manejar SVG
            if ext == '.svg':
                png_data = cairosvg.svg2png(url=file_path)
                return Image.open(io.BytesIO(png_data))
            # Manejar formatos comunes
            else:
                return Image.open(file_path)
        except Exception as e:
            print(f"Error cargando imagen {file_path}: {e}")
            return None
    
    def resize_to_fit(self, image, target_width, target_height):
        """Redimensionar una imagen manteniendo proporción para ajustarse al área objetivo"""
        # Obtener dimensiones originales
        width, height = image.size
        
        # Calcular ratios de escalado
        width_ratio = target_width / width
        height_ratio = target_height / height
        
        # Usar el ratio más pequeño para asegurar que cabe en el área
        ratio = min(width_ratio, height_ratio)
        
        # Calcular nuevas dimensiones
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        # Redimensionar
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def apply_realistic_effects(self, base, design, x, y):
        """Aplicar efectos realistas para integrar el diseño con la base"""
        # Paso 1: Ajustar el contraste y brillo del diseño
        enhancer = ImageEnhance.Contrast(design)
        design = enhancer.enhance(0.95)  # Ligera reducción de contraste
        
        enhancer = ImageEnhance.Brightness(design)
        design = enhancer.enhance(0.9)  # Ligera reducción de brillo
        
        # Paso 2: Extraer textura de la base para aplicarla al diseño
        design_width, design_height = design.size
        texture_area = base.crop((x, y, x + design_width, y + design_height))
        
        # Paso 3: Crear una máscara del diseño (para mantener su forma)
        r, g, b, a = design.split()
        
        # Paso 4: Aplicar un ligero desenfoque para suavizar bordes
        design = design.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Paso 5: Mezclar la textura con el diseño
        result = base.copy()
        
        # Crear una capa para la textura
        texture_layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
        texture_layer.paste(design, (x, y), design)
        
        # Mezclar capas con blend mode
        # Simular overlay blend mode
        result = Image.alpha_composite(result, texture_layer)
        
        # Paso 6: Aplicar un ligero desenfoque para simular integración
        blurred_area = result.crop((x, y, x + design_width, y + design_height))
        blurred_area = blurred_area.filter(ImageFilter.GaussianBlur(radius=0.3))
        result.paste(blurred_area, (x, y))
        
        return result

class MockupGenerator:
    def __init__(self):
        self.base_image = None
        self.design_images = []
        self.result_images = []
        self.target_area = (0, 0, 0, 0)  # x, y, width, height
        
    def load_base_image(self, path):
        """Cargar la imagen base desde una ruta"""
        try:
            self.base_image = Image.open(path)
            return True
        except Exception as e:
            print(f"Error al cargar la imagen base: {e}")
            return False
    
    def load_design_images(self, paths):
        """Cargar múltiples imágenes de diseño"""
        self.design_images = []
        successful_loads = 0
        
        for path in paths:
            try:
                # Según la extensión, cargar de forma diferente
                ext = os.path.splitext(path)[1].lower()
                
                if ext == '.svg':
                    # Convertir SVG a PNG usando cairosvg
                    png_data = cairosvg.svg2png(url=path)
                    img = Image.open(io.BytesIO(png_data))
                else:
                    # Cargar formatos normales con PIL
                    img = Image.open(path)
                
                # Asegurar que la imagen tenga canal alpha (transparencia)
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                self.design_images.append((path, img))
                successful_loads += 1
            except Exception as e:
                print(f"Error al cargar el diseño {path}: {e}")
        
        return successful_loads
    
    def set_target_area(self, x, y, width, height):
        """Establecer el área donde se colocarán los diseños"""
        self.target_area = (x, y, width, height)
    
    def generate_mockups(self, apply_effects=False, output_folder="./mockups"):
        """Generar múltiples mockups con los diseños cargados"""
        if self.base_image is None or not self.design_images:
            return False, "No hay imagen base o diseños cargados"
        
        self.result_images = []
        
        try:
            # Crear carpeta de salida si no existe
            os.makedirs(output_folder, exist_ok=True)
            
            for path, design in self.design_images:
                # Redimensionar el diseño para ajustarse al área objetivo
                design_resized = self.resize_to_fit(design, 
                                                   self.target_area[2], 
                                                   self.target_area[3])
                
                # Crear copia de la imagen base
                result = self.base_image.copy()
                if result.mode != 'RGBA':
                    result = result.convert('RGBA')
                
                # Aplicar efectos si se solicita
                if apply_effects:
                    result = self.apply_realistic_effects(result, design_resized, 
                                                        self.target_area[0], 
                                                        self.target_area[1])
                else:
                    # Pegar el diseño en la posición correspondiente
                    result.paste(design_resized, 
                              (self.target_area[0], self.target_area[1]), 
                              design_resized)
                
                # Guardar el resultado
                output_path = os.path.join(output_folder, 
                                         f"mockup_{os.path.splitext(os.path.basename(path))[0]}.png")
                result.save(output_path)
                
                # Almacenar el resultado
                self.result_images.append((output_path, result))
            
            return True, self.result_images
        except Exception as e:
            print(f"Error al generar los mockups: {e}")
            return False, str(e)
    
    def resize_to_fit(self, image, target_width, target_height):
        """Redimensionar una imagen manteniendo proporción para ajustarse al área objetivo"""
        # Obtener dimensiones originales
        width, height = image.size
        
        # Calcular ratios de escalado
        width_ratio = target_width / width
        height_ratio = target_height / height
        
        # Usar el ratio más pequeño para asegurar que cabe en el área
        ratio = min(width_ratio, height_ratio)
        
        # Calcular nuevas dimensiones
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        # Redimensionar
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def apply_realistic_effects(self, base, design, x, y):
        """Aplicar efectos realistas para integrar el diseño con la base"""
        # Paso 1: Ajustar el contraste y brillo del diseño
        enhancer = ImageEnhance.Contrast(design)
        design = enhancer.enhance(0.95)  # Ligera reducción de contraste
        
        enhancer = ImageEnhance.Brightness(design)
        design = enhancer.enhance(0.9)  # Ligera reducción de brillo
        
        # Paso 2: Extraer textura de la base para aplicarla al diseño
        design_width, design_height = design.size
        texture_area = base.crop((x, y, x + design_width, y + design_height))
        
        # Paso 3: Crear una máscara del diseño (para mantener su forma)
        r, g, b, a = design.split()
        
        # Paso 4: Aplicar un ligero desenfoque para suavizar bordes
        design = design.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Paso 5: Mezclar la textura con el diseño
        result = base.copy()
        
        # Crear una capa para la textura
        texture_layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
        texture_layer.paste(design, (x, y), design)
        
        # Mezclar capas con blend mode
        # Simular overlay blend mode
        result = Image.alpha_composite(result, texture_layer)
        
        # Paso 6: Aplicar un ligero desenfoque para simular integración
        blurred_area = result.crop((x, y, x + design_width, y + design_height))
        blurred_area = blurred_area.filter(ImageFilter.GaussianBlur(radius=0.3))
        result.paste(blurred_area, (x, y))
        
        return result

class AreaSelector(QWidget):
    """Widget para seleccionar un área en una imagen"""
    area_changed = pyqtSignal(QRect)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.begin = QPoint()
        self.end = QPoint()
        self.selecting = False
        self.selected_area = QRect()
        self.image = None
        
    def set_image(self, pixmap):
        """Establecer la imagen sobre la que seleccionar"""
        self.image = pixmap
        self.update()
        
    def paintEvent(self, event):
        """Dibujar la imagen y el área seleccionada"""
        if not self.image:
            return
            
        painter = QPainter(self)
        
        # Dibujar la imagen
        painter.drawPixmap(0, 0, self.image)
        
        # Dibujar el área seleccionada si existe
        if not self.selected_area.isNull():
            # Dibuja un rectángulo semitransparente
            painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.PenStyle.DashLine))
            painter.setBrush(QBrush(QColor(255, 0, 0, 50)))
            painter.drawRect(self.selected_area)
            
    def mousePressEvent(self, event):
        """Iniciar la selección de área"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.begin = event.pos()
            self.end = event.pos()
            self.selecting = True
            self.update()
            
    def mouseMoveEvent(self, event):
        """Actualizar el área mientras se arrastra"""
        if self.selecting:
            self.end = event.pos()
            self.selected_area = QRect(self.begin, self.end).normalized()
            self.update()
            
    def mouseReleaseEvent(self, event):
        """Finalizar la selección del área"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.end = event.pos()
            self.selecting = False
            self.selected_area = QRect(self.begin, self.end).normalized()
            self.update()
            
            # Emitir señal con el área seleccionada
            self.area_changed.emit(self.selected_area)
            
    def get_selected_area(self):
        """Obtener el área seleccionada"""
        return self.selected_area

class MockupGeneratorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.mockup_generator = MockupGenerator()
        self.base_image_path = None
        self.design_paths = []
        self.selected_area = QRect()
        self.output_folder = os.path.join(os.path.expanduser("~"), "Mockups")
        
        self.init_ui()
        
    def init_ui(self):
        """Inicializar la interfaz de usuario"""
        self.setWindowTitle("Generador Avanzado de Mockups")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central con splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Splitter para dividir la pantalla
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Panel izquierdo (controles)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Grupo para cargar imágenes
        load_group = QGroupBox("Cargar Imágenes")
        load_layout = QVBoxLayout()
        
        # Botón para cargar imagen base
        self.btn_load_base = QPushButton("Cargar Imagen Base")
        self.btn_load_base.clicked.connect(self.load_base_image)
        load_layout.addWidget(self.btn_load_base)
        
        self.base_label = QLabel("Ninguna imagen base cargada")
        load_layout.addWidget(self.base_label)
        
        # Botón para cargar diseño individual
        self.btn_load_design = QPushButton("Cargar Diseño Individual")
        self.btn_load_design.clicked.connect(self.load_design_image)
        load_layout.addWidget(self.btn_load_design)
        
        # Botón para cargar carpeta de diseños
        self.btn_load_designs_folder = QPushButton("Cargar Carpeta de Diseños")
        self.btn_load_designs_folder.clicked.connect(self.load_designs_folder)
        load_layout.addWidget(self.btn_load_designs_folder)
        
        # Lista de diseños cargados
        self.design_list_label = QLabel("Diseños Cargados:")
        load_layout.addWidget(self.design_list_label)
        
        self.design_list = QListWidget()
        self.design_list.setMaximumHeight(150)
        load_layout.addWidget(self.design_list)
        
        load_group.setLayout(load_layout)
        left_layout.addWidget(load_group)
        
        # Grupo para opciones avanzadas
        options_group = QGroupBox("Opciones Avanzadas")
        options_layout = QVBoxLayout()
        
        # Checkbox para efectos realistas
        self.chk_realistic = QCheckBox("Aplicar Efectos Realistas")
        self.chk_realistic.setChecked(True)
        options_layout.addWidget(self.chk_realistic)
        
        # Botón para seleccionar carpeta de salida
        self.btn_output_folder = QPushButton("Seleccionar Carpeta de Salida")
        self.btn_output_folder.clicked.connect(self.select_output_folder)
        options_layout.addWidget(self.btn_output_folder)
        
        self.output_folder_label = QLabel(f"Carpeta: {self.output_folder}")
        options_layout.addWidget(self.output_folder_label)
        
        options_group.setLayout(options_layout)
        left_layout.addWidget(options_group)
        
        # Botones de acción
        actions_group = QGroupBox("Acciones")
        actions_layout = QVBoxLayout()
        
        self.btn_process = QPushButton("Procesar Todos los Diseños")
        self.btn_process.clicked.connect(self.process_all_designs)
        self.btn_process.setEnabled(False)
        actions_layout.addWidget(self.btn_process)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        actions_layout.addWidget(self.progress_bar)
        
        actions_group.setLayout(actions_layout)
        left_layout.addWidget(actions_group)
        
        # Agrega expansión al final para que todo se ajuste correctamente
        left_layout.addStretch()
        
        # Panel derecho (editor y previsualizaciones)
        right_panel = QTabWidget()
        
        # Tab para edición/selección de área
        self.editor_tab = QWidget()
        editor_layout = QVBoxLayout(self.editor_tab)
        
        # Instrucciones para selección de área
        select_instructions = QLabel("Selecciona el área donde se colocarán los diseños:")
        editor_layout.addWidget(select_instructions)
        
        # Widget para seleccionar área
        self.area_selector = AreaSelector()
        self.area_selector.area_changed.connect(self.update_selected_area)
        
        # Scroll area para la imagen
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.area_selector)
        editor_layout.addWidget(scroll_area)
        
        # Información del área seleccionada
        self.area_info = QLabel("Área seleccionada: Ninguna")
        editor_layout.addWidget(self.area_info)
        
        right_panel.addTab(self.editor_tab, "Editor")
        
        # Tab para resultados
        self.results_tab = QWidget()
        results_layout = QVBoxLayout(self.results_tab)
        
        self.results_label = QLabel("Resultados:")
        results_layout.addWidget(self.results_label)
        
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.open_result)
        results_layout.addWidget(self.results_list)
        
        # Vista previa del resultado seleccionado
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(QSize(400, 400))
        
        # Scroll area para la vista previa
        preview_scroll = QScrollArea()
        preview_scroll.setWidgetResizable(True)
        preview_scroll.setWidget(self.preview_label)
        results_layout.addWidget(preview_scroll)
        
        right_panel.addTab(self.results_tab, "Resultados")
        
        # Añadir paneles al splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Establecer proporciones iniciales del splitter
        splitter.setSizes([300, 900])
        
    def load_base_image(self):
        """Abrir diálogo para seleccionar imagen base"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen Base", "", 
            "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            if self.mockup_generator.load_base_image(file_path):
                self.base_image_path = file_path
                self.base_label.setText(f"Base: {os.path.basename(file_path)}")
                
                # Mostrar la imagen en el selector de área
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    # Mostrar miniatura en el label
                    scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
                    self.base_label.setPixmap(scaled_pixmap)
                    
                    # Mostrar imagen completa en el selector de área
                    self.area_selector.set_image(pixmap)
                    self.area_selector.setMinimumSize(pixmap.size())
                
                # Resetear área seleccionada
                self.selected_area = QRect()
                self.area_info.setText("Área seleccionada: Ninguna")
            else:
                QMessageBox.critical(self, "Error", "No se pudo cargar la imagen base.")
    
    def load_design_image(self):
        """Abrir diálogo para seleccionar imagen de diseño individual"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Seleccionar Diseños", "", 
            "Imágenes (*.png *.jpg *.jpeg *.svg)"
        )
        
        if file_paths:
            self.add_designs_to_list(file_paths)
    
    def load_designs_folder(self):
        """Abrir diálogo para seleccionar carpeta con diseños"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Seleccionar Carpeta de Diseños"
        )
        
        if folder_path:
            # Obtener todos los archivos de imagen en la carpeta
            design_files = []
            for root, _, files in os.walk(folder_path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in ['.png', '.jpg', '.jpeg', '.svg']:
                        design_files.append(os.path.join(root, file))
            
            if design_files:
                self.add_designs_to_list(design_files)
            else:
                QMessageBox.warning(self, "Aviso", 
                                   "No se encontraron archivos de imagen en la carpeta seleccionada.")
    
    def add_designs_to_list(self, file_paths):
        """Añadir diseños a la lista y al generador"""
        # Guardar rutas actuales
        current_paths = self.design_paths.copy()
        
        # Añadir nuevas rutas
        for path in file_paths:
            if path not in self.design_paths:
                self.design_paths.append(path)
                self.design_list.addItem(os.path.basename(path))
        
        # Actualizar la lista en la GUI
        self.design_list_label.setText(f"Diseños Cargados: {len(self.design_paths)}")
        
        # Activar botón de proceso si hay diseños y área seleccionada
        self.btn_process.setEnabled(
            len(self.design_paths) > 0 and not self.selected_area.isNull()
        )
    
    def update_selected_area(self, rect):
        """Actualizar información del área seleccionada"""
        self.selected_area = rect
        self.area_info.setText(
            f"Área seleccionada: X={rect.x()}, Y={rect.y()}, "
            f"Ancho={rect.width()}, Alto={rect.height()}"
        )
        
        # Activar botón de proceso si hay diseños
        self.btn_process.setEnabled(len(self.design_paths) > 0)
    
    def select_output_folder(self):
        """Seleccionar carpeta donde guardar los mockups generados"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Seleccionar Carpeta de Salida", self.output_folder
        )
        
        if folder_path:
            self.output_folder = folder_path
            self.output_folder_label.setText(f"Carpeta: {self.output_folder}")
    
    def process_all_designs(self):
        """Procesar todos los diseños cargados"""
        if not self.base_image_path:
            QMessageBox.warning(self, "Advertencia", "Debe cargar una imagen base.")
            return
            
        if not self.design_paths:
            QMessageBox.warning(self, "Advertencia", "Debe cargar al menos un diseño.")
            return
            
        if self.selected_area.isNull():
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar un área para los diseños.")
            return
        
        # Configurar el área objetivo en el generador
        target_area = (
            self.selected_area.x(), 
            self.selected_area.y(),
            self.selected_area.width(),
            self.selected_area.height()
        )
        
        # Limpiar lista de resultados
        self.results_list.clear()
        self.preview_label.clear()
        
        # Mostrar barra de progreso
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # Iniciar el proceso en segundo plano
        self.processor = ImageProcessor(
            self.mockup_generator.base_image,
            self.design_paths,
            target_area,
            self.chk_realistic.isChecked(),
            self.output_folder
        )
        
        # Conectar señales
        self.processor.progress_updated.connect(self.update_progress)
        self.processor.processing_complete.connect(self.processing_finished)
        
        # Deshabilitar botones durante el procesamiento
        self.btn_process.setEnabled(False)
        self.btn_load_base.setEnabled(False)
        self.btn_load_design.setEnabled(False)
        self.btn_load_designs_folder.setEnabled(False)
        
        # Iniciar el proceso
        self.processor.start()
    
    def update_progress(self, value):
        """Actualizar la barra de progreso"""
        self.progress_bar.setValue(value)
    
    def processing_finished(self, results):
        """Gestionar la finalización del procesamiento"""
        # Habilitar botones
        self.btn_process.setEnabled(True)
        self.btn_load_base.setEnabled(True)
        self.btn_load_design.setEnabled(True)
        self.btn_load_designs_folder.setEnabled(True)
        
        # Ocultar barra de progreso
        self.progress_bar.setVisible(False)
        
        # Añadir resultados a la lista
        for filepath, _ in results:
            self.results_list.addItem(os.path.basename(filepath))
        
         # Mostrar mensaje de éxito
        QMessageBox.information(
            self, "Proceso Completado", 
            f"Se han generado {len(results)} mockups en la carpeta:\n{self.output_folder}"
        )
        
        # Cambiar a la pestaña de resultados
        parent = self.parent() if self.parent() else self
        tab_widget = parent.findChild(QTabWidget)
        if tab_widget:
            tab_widget.setCurrentIndex(1)  # Cambiar a la pestaña de resultados
    
    def open_result(self, item):
        """Mostrar la vista previa del resultado seleccionado"""
        result_file = os.path.join(self.output_folder, item.text())
        
        if os.path.exists(result_file):
            pixmap = QPixmap(result_file)
            if not pixmap.isNull():
                self.preview_label.setPixmap(pixmap.scaled(
                    self.preview_label.width(),
                    self.preview_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio
                ))
                
                # Opcional: Abrir el archivo con el visor predeterminado del sistema
                # import subprocess
                # subprocess.Popen(['start', result_file], shell=True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MockupGeneratorWindow()
    window.show()
    sys.exit(app.exec())