from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow
from estilo.estilo import obtener_estilos
from utils.dependency_checker import check_dependencies

import sys
import os

def setup_application():
    """Configura la aplicación principal"""
    app = QApplication(sys.argv)
    app.setStyleSheet(obtener_estilos())
    
    # Configurar icono de la aplicación
    icon_path = os.path.join(os.path.dirname(__file__), "recursos", "icono.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    return app

def main():
    """Función principal de la aplicación"""
    # Verificar dependencias
    check_dependencies(['Pillow', 'qrcode[pil]'])
    
    # Iniciar aplicación
    app = setup_application()
    
    try:
        ventana = MainWindow()
        ventana.show()
        return app.exec()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())