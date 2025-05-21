from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, 
                           QHBoxLayout, QMenuBar, QStatusBar, 
                           QToolBar, QDockWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon

# Importamos los módulos existentes
from modulos.productos import ProductosWindow
from modulos.redes import RedesWindow
from modulos.reescalado import ReescaladoWindow
#from modulos.MockupGenerator import MockupGeneratorWindow
from modulos.qr_generator import QrGeneratorWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hub-Skill")
        self.setMinimumSize(1200, 800)
        
        # Configurar la interfaz principal
        self.setup_ui()
        
    def setup_ui(self):
        # Crear el widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Configurar componentes principales
        self.setup_menubar()
        self.setup_toolbar()
        self.setup_left_panel()
        self.setup_right_panel()
        self.setup_statusbar()
        
    def setup_menubar(self):
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")
        
        # Acción Nuevo Producto
        new_product_action = QAction("Nuevo Producto", self)
        new_product_action.setShortcut("Ctrl+N")
        new_product_action.triggered.connect(self.abrir_productos)
        file_menu.addAction(new_product_action)
        
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Salir")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # Menú Herramientas
        tools_menu = menubar.addMenu("&Herramientas")
        
        # Redes Sociales
        redes_action = QAction("Redes Sociales", self)
        redes_action.triggered.connect(self.abrir_redes)
        tools_menu.addAction(redes_action)
        
        # Reescalado de Imágenes
        reescalado_action = QAction("Reescalado de Imágenes", self)
        reescalado_action.triggered.connect(self.abrir_reescalado)
        tools_menu.addAction(reescalado_action)
        
        # MockupGenerator
        mockup_action = QAction("MockupGenerator", self)
        mockup_action.triggered.connect(self.abrir_MockupGenerator)
        tools_menu.addAction(mockup_action)
        
        # Código QR
        qr_action = QAction("Código QR", self)
        qr_action.triggered.connect(self.abrir_qr)
        tools_menu.addAction(qr_action)
        
    def setup_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Botones de la barra de herramientas con iconos
        productos_action = QAction("📦 Productos", self)
        productos_action.triggered.connect(self.abrir_productos)
        toolbar.addAction(productos_action)
        
        redes_action = QAction("🌐 Redes", self)
        redes_action.triggered.connect(self.abrir_redes)
        toolbar.addAction(redes_action)
        
        reescalado_action = QAction("🖼️ Reescalar", self)
        reescalado_action.triggered.connect(self.abrir_reescalado)
        toolbar.addAction(reescalado_action)
        
        mockup_action = QAction("🧮 Mockup", self)
        mockup_action.triggered.connect(self.abrir_MockupGenerator)
        toolbar.addAction(mockup_action)
        
        qr_action = QAction("📱 QR", self)
        qr_action.triggered.connect(self.abrir_qr)
        toolbar.addAction(qr_action)
        
    def setup_left_panel(self):
        left_dock = QDockWidget("Navegación", self)
        left_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        
        # Widget para el panel izquierdo
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Botones de navegación
        productos_label = QLabel("📦 Productos")
        productos_label.setStyleSheet("font-size: 14pt; padding: 5px;")
        left_layout.addWidget(productos_label)
        
        redes_label = QLabel("🌐 Redes Sociales")
        redes_label.setStyleSheet("font-size: 14pt; padding: 5px;")
        left_layout.addWidget(redes_label)
        
        reescalado_label = QLabel("🖼️ Reescalado")
        reescalado_label.setStyleSheet("font-size: 14pt; padding: 5px;")
        left_layout.addWidget(reescalado_label)
        
        mockup_label = QLabel("🧮 MockupGenerator")
        mockup_label.setStyleSheet("font-size: 14pt; padding: 5px;")
        left_layout.addWidget(mockup_label)
        
        qr_label = QLabel("📱 Código QR")
        qr_label.setStyleSheet("font-size: 14pt; padding: 5px;")
        left_layout.addWidget(qr_label)
        
        left_layout.addStretch()
        left_dock.setWidget(left_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, left_dock)
        
    def setup_right_panel(self):
        right_dock = QDockWidget("Detalles", self)
        right_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        
        # Widget para el panel derecho
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        info_label = QLabel("Panel de Información")
        info_label.setStyleSheet("font-size: 14pt; padding: 5px;")
        right_layout.addWidget(info_label)
        
        right_layout.addStretch()
        right_dock.setWidget(right_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right_dock)
        
    def setup_statusbar(self):
        status = QStatusBar()
        self.setStatusBar(status)
        status.showMessage("Bienvenido a Hub-Skill")

    # Mantenemos los métodos existentes para abrir las ventanas
    def abrir_productos(self):
        """Función para abrir la ventana de productos"""
        self.productos_window = ProductosWindow()
        self.productos_window.show()

    def abrir_redes(self):
        """Función para abrir la ventana de redes sociales"""
        self.redes_window = RedesWindow()
        self.redes_window.show()
        
    def abrir_reescalado(self):
        """Función para abrir la ventana de reescalado de imágenes"""
        self.reescalado_window = ReescaladoWindow()
        self.reescalado_window.show()

    def abrir_MockupGenerator(self):
        """Función para abrir la MockupGenerator"""
        self.MockupGenerator_window = MockupGeneratorWindow()
        self.MockupGenerator_window.show()

    def abrir_qr(self):
        """Función para abrir la ventana de generación de QR"""
        self.qr_window = QrGeneratorWindow()
        self.qr_window.show()