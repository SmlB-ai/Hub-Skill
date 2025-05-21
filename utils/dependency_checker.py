import subprocess
import sys
from typing import List, Dict

def check_dependencies(required_packages: List[str]) -> Dict[str, bool]:
    """
    Verifica y instala las dependencias necesarias.
    
    Args:
        required_packages: Lista de paquetes a verificar/instalar
    
    Returns:
        Dict con el estado de instalación de cada paquete
    """
    results = {}
    
    for package in required_packages:
        try:
            __import__(package.split('[')[0])  # Maneja casos como 'qrcode[pil]'
            results[package] = True
        except ImportError:
            print(f"Instalando {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                results[package] = True
            except subprocess.CalledProcessError as e:
                print(f"Error instalando {package}: {e}")
                results[package] = False
    
    return results