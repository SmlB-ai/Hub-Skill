from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from ui.components.navigation_panel import NavigationPanel
from ui.components.inicio_panel import InicioPanel
from modulos.productos import ProductosWindow
from modulos.sku import SkuWindow
from modulos.reescalado import ReescaladoWindow
from modulos.mockup_generator import MockupGeneratorWindow
from modulos.qr_generator import QrGeneratorWindow
from modulos.urls import UrlsWindow
from modulos.medidas import MedidasWindow
from modulos.precios import PreciosWindow   # <--- NUEVO: importa tu módulo de precios

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hub-Skill")
        self.setMinimumSize(1200, 800)

        # Layout principal
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Barra de navegación
        self.navigation_panel = NavigationPanel()
        main_layout.addWidget(self.navigation_panel)

        # Área central apilada
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)

        # Instanciar los módulos como widgets/paneles
        self.inicio_panel = InicioPanel()
        self.productos_widget = ProductosWindow()
        self.sku_widget = SkuWindow()
        self.reescalado_widget = ReescaladoWindow()
        self.urls_widget = UrlsWindow()
        self.qr_widget = QrGeneratorWindow()
        self.mockup_widget = MockupGeneratorWindow()
        self.medidas_widget = MedidasWindow()
        self.precios_widget = PreciosWindow()  # <--- NUEVO: instancia tu módulo

        # Agregar los paneles al stacked_widget en el ORDEN DEL FLUJO
        self.stacked_widget.addWidget(self.inicio_panel)        # index 0 - Panel de inicio
        self.stacked_widget.addWidget(self.productos_widget)    # index 1 - Datos de producto
        self.stacked_widget.addWidget(self.sku_widget)          # index 2 - SKU y Códigos
        self.stacked_widget.addWidget(self.reescalado_widget)   # index 3 - Imágenes
        self.stacked_widget.addWidget(self.urls_widget)         # index 4 - URLs
        self.stacked_widget.addWidget(self.qr_widget)           # index 5 - Publicar/Exportar
        self.stacked_widget.addWidget(self.mockup_widget)       # index 6 - Mockup Generator
        self.stacked_widget.addWidget(self.medidas_widget)      # index 7 - Medidas de Producto
        self.stacked_widget.addWidget(self.precios_widget)      # index 8 - Precios y Dinero  <--- NUEVA posición

        # --- CONEXIONES DE NAVEGACIÓN ---
        self.navigation_panel.inicio_clicked.connect(self.ir_a_inicio)
        self.navigation_panel.productos_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.navigation_panel.sku_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.navigation_panel.imagenes_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        self.navigation_panel.urls_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        self.navigation_panel.publicar_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(5))
        self.navigation_panel.medidas_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(7))
        self.navigation_panel.precios_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(8))  # <--- NUEVO

        # Flujo guiado: botón "nuevo producto" en panel de inicio lleva a Datos de producto
        self.inicio_panel.nuevo_producto_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

    def ir_a_inicio(self):
        self.inicio_panel.actualizar_estadisticas()
        self.stacked_widget.setCurrentIndex(0)