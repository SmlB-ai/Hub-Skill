from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from botones.botones import crear_boton
from modulos.productos import ProductosWindow
from modulos.redes import RedesWindow
from modulos.reescalado import ReescaladoWindow
from modulos.MockupGenerator import MockupGeneratorWindow
from modulos.qr_generator import QrGeneratorWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplicación Modular")
        self.setMinimumSize(800, 600)

        main_layout = QVBoxLayout()

        # Mensaje de bienvenida con mejor estilo
        welcome_frame = QFrame()
        welcome_frame.setStyleSheet("background-color: #333; border-radius: 15px; padding: 20px;")
        welcome_layout = QVBoxLayout()
        
        bienvenida_label = QLabel("¡Hola! ¿Qué vamos a hacer hoy?")
        bienvenida_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #4CAF50;")
        bienvenida_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(bienvenida_label)
        
        welcome_frame.setLayout(welcome_layout)
        main_layout.addWidget(welcome_frame)

        # Contenedor para los botones con diseño mejorado
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)  # Espacio entre botones

        # Botón de productos
        productos_boton = crear_boton("Productos", self.abrir_productos, "📦")
        button_layout.addWidget(productos_boton)

        # Botón de redes sociales
        redes_boton = crear_boton("Redes Sociales", self.abrir_redes, "🌐")
        button_layout.addWidget(redes_boton)
        
        # Nuevo botón para reescalado de imágenes
        reescalado_boton = crear_boton("Reescalado de Imágenes", self.abrir_reescalado, "🖼️")
        button_layout.addWidget(reescalado_boton)

        # Nuevo botón para MockupGenerator
        MockupGenerator_boton = crear_boton("MockupGenerator", self.abrir_MockupGenerator, "🧮")
        button_layout.addWidget(MockupGenerator_boton)

        # boton Qr
        qr_boton =crear_boton("Codigo QR", self.abrir_qr, "📱")
        button_layout.addWidget(qr_boton)   

        main_layout.addLayout(button_layout)
        
        # Añadimos un pie de página
        footer = QLabel("Desarrollado con ❤️ - 2025")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("margin-top: 30px; color: #888;")
        main_layout.addWidget(footer)

        self.setLayout(main_layout)

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