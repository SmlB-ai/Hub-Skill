from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from ui.components.navigation_panel import NavigationPanel
from ui.components.inicio_panel import InicioPanel
from modulos.productos import ProductosWindow
from modulos.sku import SkuWindow
from modulos.reescalado import ReescaladoWindow
from modulos.mockup_generator import MockupGeneratorWindow
from modulos.qr_generator import QrGeneratorWindow

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
        self.mockup_widget = MockupGeneratorWindow()
        self.qr_widget = QrGeneratorWindow()

        # Agregar los paneles al stacked_widget en el ORDEN DEL FLUJO
        self.stacked_widget.addWidget(self.inicio_panel)        # index 0 - Panel de inicio
        self.stacked_widget.addWidget(self.productos_widget)    # index 1 - Datos de producto
        self.stacked_widget.addWidget(self.sku_widget)     # index 2 - SKU y Códigos (cámbialo por tu panel SKU cuando lo tengas)
        self.stacked_widget.addWidget(self.reescalado_widget)   # index 3 - Imágenes
        self.stacked_widget.addWidget(self.mockup_widget)       # index 4 - URLs (cámbialo por tu panel URLs cuando lo tengas)
        self.stacked_widget.addWidget(self.qr_widget)           # index 5 - Publicar/Exportar (cámbialo por tu panel Publicar cuando lo tengas)

        # --- CONEXIONES DE NAVEGACIÓN ---
        # Panel de inicio: refresca estadísticas cada vez que se muestra
        self.navigation_panel.inicio_clicked.connect(self.ir_a_inicio)
        # Resto de navegación
        self.navigation_panel.productos_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.navigation_panel.sku_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.navigation_panel.imagenes_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        self.navigation_panel.urls_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        self.navigation_panel.publicar_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(5))

        # Flujo guiado: botón "nuevo producto" en panel de inicio lleva a Datos de producto
        self.inicio_panel.nuevo_producto_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

    def ir_a_inicio(self):
        # Este método asegura que el panel de inicio siempre muestre estadísticas actualizadas
        self.inicio_panel.actualizar_estadisticas()
        self.stacked_widget.setCurrentIndex(0)