# file_generator.py
import threading
import os
import re
import pyperclip
import time
from datetime import datetime # <--- Importar datetime

class FileGenerator(threading.Thread):
    def __init__(self, base_path):
        super().__init__()
        self.base_directory = base_path
        self.running = False
        self.daemon = True
        self.last_clipboard_content = ""

        # Expresiones regulares actualizadas para detección de rutas
        self.comment_patterns = [
            r"^//\s*(.+)",        # JavaScript, TypeScript, etc.
            r"^#\s*(.+)",         # Python, Bash
            r"^--\s*(.+)",        # SQL, Lua
            r"^/\*\s*(.+)\*/",    # CSS/JS block comments
            r"^<!--\s*(.+)-->"    # HTML/XML
        ]

    def stop(self):
        self.running = False

    def extract_file_path_from_comment(self, content):
        for pattern in self.comment_patterns:
            match = re.match(pattern, content)
            if match:
                return match.group(1).strip()
        return None

    def create_file(self, full_path, content):
        try:
            # Limpiar contenido manteniendo estructura
            cleaned_content = []
            for line in content.split('\n'):
                if re.match(r'^\s*$', line):
                    cleaned_content.append('')
                else:
                    cleaned_content.append(line.rstrip())

            # Crear directorios y archivo
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, 'w', encoding='utf-8') as file:
                file.write('\n'.join(cleaned_content))

            # --- Cambio: Añadir fecha y hora al mensaje de log ---
            now = datetime.now()
            timestamp = now.strftime("%d/%m/%Y %H:%M:%S") # Formato DD/MM/YYYY HH:MM:SS
            relative_path = os.path.relpath(full_path, self.base_directory).replace("\\", "/")
            print(f"[{timestamp}] Archivo generado: {relative_path}")
            # --- Fin Cambio ---
            return True
        except Exception as e:
            print(f"[File Generator Error] {str(e)}")
            return False

    def run(self):
        self.running = True
        print("[File Generator] Iniciando monitorización del portapapeles...")

        while self.running:
            try:
                clipboard_content = pyperclip.paste()

                if clipboard_content != self.last_clipboard_content:
                    self.last_clipboard_content = clipboard_content

                    relative_path = self.extract_file_path_from_comment(clipboard_content)
                    if relative_path:
                        full_path = os.path.normpath(os.path.join(self.base_directory, relative_path))

                        # Verificar que está dentro del directorio base
                        if os.path.commonpath([self.base_directory]) != os.path.commonpath([self.base_directory, full_path]):
                            print("[File Generator] Intento de escribir fuera del directorio base bloqueado")
                            continue
                        # --- NUEVA COMPROBACIÓN: Verificar si el archivo tiene extensión ---
                        if not os.path.splitext(full_path)[1]:
                            print(f"[File Generator] Bloqueado: El archivo '{relative_path}' no tiene extensión.")
                            continue # Saltar la creación si no hay extensión
                        # --- FIN NUEVA COMPROBACIÓN ---
                        self.create_file(full_path, clipboard_content)

                time.sleep(0.5)
            except Exception as e:
                print(f"[File Generator Error] {str(e)}")
                time.sleep(1)

        print("[File Generator] Monitorización detenida")