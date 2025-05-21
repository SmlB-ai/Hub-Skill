from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
import webbrowser

class RedesWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # 🪪 Configuración general de la ventana
        self.setWindowTitle("Redes Sociales de SkillHub")
        self.setMinimumSize(400, 300)

        # 🧱 Layout principal vertical
        layout = QVBoxLayout()

        # 👋 Etiqueta de bienvenida
        saludo = QLabel("Aquí puedes acceder a nuestras redes sociales:")
        layout.addWidget(saludo)

        # 🔗 Botón para abrir Facebook
        boton_facebook = QPushButton("📘 Ir a Facebook")
        boton_facebook.clicked.connect(lambda: webbrowser.open("https://www.facebook.com/people/SkillHub/61561024439753/"))
        layout.addWidget(boton_facebook)

        # 📸 Botón para abrir Instagram
        boton_instagram = QPushButton("📸 Ir a Instagram")
        boton_instagram.clicked.connect(lambda: webbrowser.open("https://www.instagram.com/skillhub_mex/"))
        layout.addWidget(boton_instagram)

        # 💾 Aplicar el layout
        self.setLayout(layout)
