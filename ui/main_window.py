from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal

class NavigationPanel(QWidget):
    """Panel de navegación interactivo"""
    
    # Señales para cada botón
    productos_clicked = pyqtSignal()
    redes_clicked = pyqtSignal()
    reescalado_clicked = pyqtSignal()
    mockup_clicked = pyqtSignal()
    qr_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Crear botones con estilo consistente
        buttons = [
            ("📦 Productos", self.productos_clicked),
            ("🌐 Redes Sociales", self.redes_clicked),
            ("🖼️ Reescalado", self.reescalado_clicked),
            ("🧮 MockupGenerator", self.mockup_clicked),
            ("📱 Código QR", self.qr_clicked)
        ]
        
        for text, signal in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 14pt;
                    padding: 10px;
                    text-align: left;
                    border: none;
                    background: transparent;
                }
                QPushButton:hover {
                    background-color: rgba(76, 175, 80, 0.1);
                }
            """)
            btn.clicked.connect(signal)
            layout.addWidget(btn)
        
        layout.addStretch()


def open_window(self, WindowClass, window_name):
    """
    Abre una ventana de manera segura con manejo de errores.
    
    Args:
        WindowClass: Clase de la ventana a abrir
        window_name: Nombre de la ventana para mensajes de error
    """
    try:
        window = WindowClass()
        window.show()
        setattr(self, f"{window_name}_window", window)
    except Exception as e:
        QMessageBox.critical(
            self,
            "Error",
            f"Error al abrir {window_name}: {str(e)}"
        )