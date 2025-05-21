from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

def crear_boton(texto, funcion, emoji=""):
    """Función para crear botones con mejor diseño y funcionalidad"""
    boton = QPushButton()
    
    # Creamos un layout vertical para organizar el emoji y el texto
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.setContentsMargins(10, 15, 10, 15)
    layout.setSpacing(10)
    
    # Añadimos el emoji
    if emoji:
        emoji_label = QLabel(emoji)
        emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        emoji_label.setStyleSheet("font-size: 32pt; color: white; background-color: transparent;")
        layout.addWidget(emoji_label)
    
    # Añadimos el texto
    texto_label = QLabel(texto)
    texto_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    texto_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: white; background-color: transparent;")
    layout.addWidget(texto_label)
    
    # Aplicamos el layout al botón
    boton.setLayout(layout)
    
    # Estilo mejorado para el botón
    boton.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border-radius: 15px;
            min-width: 180px;
            min-height: 150px;
            padding: 15px;
        }
        
        QPushButton:hover {
            background-color: #388E3C;
            border: 2px solid #A5D6A7;
        }
        
        QPushButton:pressed {
            background-color: #2E7D32;
        }
    """)
    
    # Conectamos la función
    boton.clicked.connect(funcion)
    
    return boton