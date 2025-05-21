def obtener_estilos():
    return """
    QWidget {
        background-color: #212121;  /* Fondo oscuro más elegante */
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 12pt;
        color: #F5F5F5;  /* Texto claro */
    }

    QPushButton {
        background-color: #4CAF50;  /* Verde suave */
        color: white;
        border-radius: 10px;
        padding: 10px;
        font-size: 16pt;
    }

    QPushButton:hover {
        background-color: #388E3C;  /* Verde más oscuro */
        border: 2px solid #A5D6A7;  /* Borde claro al pasar el mouse */
    }
    
    QPushButton:pressed {
        background-color: #2E7D32;  /* Verde aún más oscuro al presionar */
    }

    QLineEdit, QSpinBox, QComboBox, QSlider {
        background-color: #424242;  /* Gris oscuro para entradas */
        color: #F5F5F5;  /* Texto claro en las entradas */
        border-radius: 5px;
        padding: 8px;
        font-size: 12pt;
        border: 1px solid #616161;  /* Borde visible para entradas */
    }
    
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
        border: 2px solid #66BB6A;  /* Borde destacado al enfocar */
    }
    
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 25px;
        border-left-width: 1px;
        border-left-color: #616161;
        border-left-style: solid;
        border-top-right-radius: 3px;
        border-bottom-right-radius: 3px;
    }
    
    QComboBox:on {
        padding-top: 3px;
        padding-left: 4px;
    }
    
    QComboBox QAbstractItemView {
        border: 2px solid #388E3C;
        selection-background-color: #4CAF50;
    }

    QLabel {
        color: #F5F5F5;  /* Texto claro */
        font-size: 14pt;
    }
    
    QProgressBar {
        border: 2px solid #616161;
        border-radius: 5px;
        text-align: center;
        height: 25px;
    }
    
    QProgressBar::chunk {
        background-color: #4CAF50;
        width: 10px;
        margin: 0.5px;
    }
    
    QSlider::groove:horizontal {
        border: 1px solid #999999;
        height: 8px;
        background: #424242;
        margin: 2px 0;
    }
    
    QSlider::handle:horizontal {
        background: #4CAF50;
        border: 1px solid #5c5c5c;
        width: 18px;
        margin: -2px 0;
        border-radius: 9px;
    }
    
    QFrame {
        border-radius: 10px;
    }
    
    QMessageBox {
        background-color: #212121;
    }
    
    QMessageBox QPushButton {
        min-width: 100px;
        min-height: 30px;
    }
    """