def obtener_estilos():
    return """
    QMainWindow {
        background-color: #2E3440;
        color: #ECEFF4;
    }
    
    QMenuBar {
        background-color: #3B4252;
        color: #ECEFF4;
    }
    
    QMenuBar::item:selected {
        background-color: #4C566A;
    }
    
    QToolBar {
        background-color: #3B4252;
        border: none;
        spacing: 3px;
        padding: 3px;
    }
    
    QToolButton {
        background-color: #4C566A;
        border-radius: 4px;
        padding: 5px;
    }
    
    QToolButton:hover {
        background-color: #5E81AC;
    }
    
    QDockWidget {
        border: 1px solid #4C566A;
    }
    
    QDockWidget::title {
        background: #4C566A;
        padding-left: 5px;
        padding-top: 2px;
    }
    
    QStatusBar {
        background-color: #3B4252;
        color: #ECEFF4;
    }
    
    QLabel {
        color: #ECEFF4;
    }
    """