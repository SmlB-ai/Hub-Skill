from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QMessageBox
from ui.components.navigation_panel import NavigationPanel
from modulos.productos import ProductosWindow
from modulos.redes import RedesWindow
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

        # Instanciar los módulos como widgets
        self.productos_widget = ProductosWindow()
        self.redes_widget = RedesWindow()
        self.reescalado_widget = ReescaladoWindow()
        self.mockup_widget = MockupGeneratorWindow()
        self.qr_widget = QrGeneratorWindow()

        # Agregar los módulos al stacked_widget
        self.stacked_widget.addWidget(self.productos_widget)    # index 0
        self.stacked_widget.addWidget(self.redes_widget)        # index 1
        self.stacked_widget.addWidget(self.reescalado_widget)   # index 2
        self.stacked_widget.addWidget(self.mockup_widget)       # index 3
        self.stacked_widget.addWidget(self.qr_widget)           # index 4

        # Conectar navegación
        self.navigation_panel.productos_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.navigation_panel.redes_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.navigation_panel.reescalado_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.navigation_panel.mockup_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        self.navigation_panel.qr_clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))