# main.py
import tkinter as tk
from tkinter import ttk, messagebox
from config_handler import ConfigHandler
from file_operations import FileProcessor
from main_window import MainWindow
from gui_styles import StyleManager

def configurar_tema():
    # Precargar elementos de estilo
    root = tk.Tk()
    root.withdraw()
    StyleManager()  # Inicializar estilos
    root.destroy()

def main():
    # Configuración inicial del tema
    configurar_tema()

    # Crear instancia principal
    root = tk.Tk()
    root.tk_setPalette(background='#2D2D2D', foreground='#FFFFFF')

    # Configurar manejo de excepciones globales
    def mostrar_error(exc_type, exc_value, exc_traceback):
        messagebox.showerror(
            "Error Crítico",
            f"Ocurrió un error inesperado:\n\n{str(exc_value)}"
        )

    root.report_callback_exception = mostrar_error

    # Inicializar componentes principales
    config_handler = ConfigHandler()
    file_processor = FileProcessor()

    # Aplicar estilos
    style_manager = StyleManager()

    # Crear y ejecutar ventana principal
    main_window = MainWindow(root, config_handler, file_processor)

    # Configurar cierre seguro
    def on_closing():
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir?"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()