from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from estilo.estilo import obtener_estilos

import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(obtener_estilos())  # Aplica los estilos a toda la aplicación

    ventana = MainWindow()  # Creamos la ventana principal
    ventana.show()  # Mostramos la ventana
    sys.exit(app.exec())
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QFontDatabase
from ui.main_window import MainWindow
from estilo.estilo import obtener_estilos

import sys
import os

# Aseguramos que Pillow esté instalado para el módulo de reescalado
try:
    from PIL import Image
except ImportError:
    print("La biblioteca Pillow no está instalada. Instalándola...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    print("Pillow instalado correctamente.")
    from PIL import Image

# Aseguramos que qrcode esté instalado para el módulo de códigos QR
try:
    import qrcode
except ImportError:
    print("La biblioteca qrcode no está instalada. Instalándola...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "qrcode[pil]"])
    print("qrcode instalado correctamente.")
    import qrcode

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(obtener_estilos())  # Aplica los estilos a toda la aplicación
    
    # Intenta cargar un icono para la aplicación si existe
    icon_path = os.path.join(os.path.dirname(__file__), "recursos", "icono.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    ventana = MainWindow()  # Creamos la ventana principal
    ventana.show()  # Mostramos la ventana
    sys.exit(app.exec())
    