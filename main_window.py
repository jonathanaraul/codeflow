# main_window.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import pyperclip
import os
from gui_components import (
    ScrolledText,
    CustomButton,
    LabeledEntry,
    ProjectSelector
)
from gui_styles import StyleManager
from file_generator import FileGenerator

class MainWindow:
    def __init__(self, root, config_handler, file_processor):
        self.root = root
        self.config_handler = config_handler
        self.file_processor = file_processor
        self.current_project = None
        self.incluir_ruta_var = tk.BooleanVar(value=True)
        self.generador_activo_var = tk.BooleanVar(value=False)
        self.file_generator = None

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        adjusted_height = screen_height - 70
        self.root.geometry(f"{screen_width}x{adjusted_height}+0+0")

        self.style_manager = StyleManager()
        self._setup_main_frames()
        self._create_right_panel_widgets()
        self._create_left_panel_widgets()
        self._cargar_proyectos()

    def _setup_main_frames(self):
        self.main_frame = ttk.Frame(self.root, style='TFrame', padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.right_panel = ttk.Frame(self.main_frame, style='TFrame', padding=15)
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.left_panel = ttk.Frame(self.main_frame, style='TFrame', padding=15)
        self.left_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

    def _create_right_panel_widgets(self):
        ttk.Label(self.right_panel, text="PROYECTO ACTUAL:").pack(pady=(0, 10), anchor=tk.W)
        self.project_selector = ProjectSelector(
            self.right_panel,
            self.style_manager,
            [],
            self._nuevo_proyecto
        )
        self.project_selector.frame.pack(fill=tk.X, pady=5)

        self.ruta_base_component = LabeledEntry(
            self.right_panel,
            self.style_manager,
            "RUTA BASE DEL PROYECTO:"
        )
        self.ruta_base_component.frame.pack(fill=tk.X, pady=5)

        self.btn_seleccionar = CustomButton(
            self.right_panel,
            self.style_manager,
            "📂 Seleccionar Ruta",
            self._seleccionar_ruta_base
        )
        self.btn_seleccionar.pack(pady=10, ipadx=10)

        self.prompt_text = ScrolledText(self.right_panel, self.style_manager, 6)
        ttk.Label(self.right_panel, text="PROMPT DE CONTEXTO:").pack(pady=(15, 5), anchor=tk.W)
        self.prompt_text.frame.pack(fill=tk.BOTH, expand=True)

        self.solicitud_text = ScrolledText(self.right_panel, self.style_manager, 6)
        ttk.Label(self.right_panel, text="SOLICITUD ACTUAL:").pack(pady=(15, 5), anchor=tk.W)
        self.solicitud_text.frame.pack(fill=tk.BOTH, expand=True)

        ttk.Checkbutton(
            self.right_panel,
            text="Incluir rutas y nombres de archivo",
            variable=self.incluir_ruta_var,
            style='TCheckbutton'
        ).pack(pady=(15, 5), anchor=tk.W)

        ttk.Checkbutton(
            self.right_panel,
            text="Generador de archivos",
            variable=self.generador_activo_var,
            command=self._toggle_generador_archivos,
            style='TCheckbutton'
        ).pack(pady=5, anchor=tk.W)

        self.btn_copiar = CustomButton(
            self.right_panel,
            self.style_manager,
            "⎘ Copiar y Guardar",
            self._ejecutar_copia
        )
        self.btn_copiar.pack(pady=20, ipadx=20, ipady=8)

    def _create_left_panel_widgets(self):
        ttk.Label(self.left_panel, text="CONFIGURACIÓN AVANZADA").pack(pady=(0, 15), anchor=tk.W)

        self.directorio_principal_component = LabeledEntry(
            self.left_panel,
            self.style_manager,
            "Directorio Principal (opcional):"
        )
        self.directorio_principal_component.frame.pack(fill=tk.X, pady=5)

        self.patron_component = LabeledEntry(
            self.left_panel,
            self.style_manager,
            "Patrón (opcional):"
        )
        self.patron_component.frame.pack(fill=tk.X, pady=5)

        self.archivos_text = ScrolledText(self.left_panel, self.style_manager, 4)
        ttk.Label(self.left_panel, text="Archivos Específicos:").pack(pady=(15, 5), anchor=tk.W)
        self.archivos_text.frame.pack(fill=tk.BOTH, expand=True)

        self.directorios_prohibidos_text = ScrolledText(self.left_panel, self.style_manager, 4)
        ttk.Label(self.left_panel, text="Directorios Prohibidos:").pack(pady=(15, 5), anchor=tk.W)
        self.directorios_prohibidos_text.frame.pack(fill=tk.BOTH, expand=True)

        self.archivos_prohibidos_text = ScrolledText(self.left_panel, self.style_manager, 4)
        ttk.Label(self.left_panel, text="Archivos Prohibidos:").pack(pady=(15, 5), anchor=tk.W)
        self.archivos_prohibidos_text.frame.pack(fill=tk.BOTH, expand=True)

        self.formatos_prohibidos_component = LabeledEntry(
            self.left_panel,
            self.style_manager,
            "Formatos Prohibidos:"
        )
        self.formatos_prohibidos_component.frame.pack(fill=tk.X, pady=5)

        self.project_selector.combobox.bind(
            "<<ComboboxSelected>>",
            lambda e: self._cargar_configuracion_proyecto(
                self.project_selector.get_selected()
            )
        )

    def _cargar_proyectos(self):
        proyectos = self.config_handler.get_projects()
        self.project_selector.set_projects(proyectos)
        current = self.config_handler.get_current_project()
        if current:
            self.project_selector.set_selected(current)
            self._cargar_configuracion_proyecto(current)

    def _cargar_configuracion_proyecto(self, proyecto):
        if self.file_generator and self.file_generator.is_alive():
            self.file_generator.stop()
            self.generador_activo_var.set(False)

        config = self.config_handler.get_project_config(proyecto)
        if not config:
            return

        self.ruta_base_component.set(config["ruta_base"])
        self.directorio_principal_component.set(config["directorio_principal"])
        self.archivos_text.delete()
        self.archivos_text.insert(config["archivos"])
        self.directorios_prohibidos_text.delete()
        self.directorios_prohibidos_text.insert(config["directorios_prohibidos"])
        self.archivos_prohibidos_text.delete()
        self.archivos_prohibidos_text.insert(config["archivos_prohibidos"])
        self.formatos_prohibidos_component.set(config.get("formatos_prohibidos", ""))
        self.prompt_text.delete()
        self.prompt_text.insert(config.get("prompt", ""))
        self.patron_component.set(config.get("patron", ""))
        self.solicitud_text.delete()

    def _nuevo_proyecto(self):
        nuevo_nombre = simpledialog.askstring(
            "Nuevo Proyecto",
            "Nombre del nuevo proyecto:",
            parent=self.root
        )
        if nuevo_nombre:
            try:
                self.config_handler.create_new_project(nuevo_nombre)
                self.config_handler.set_current_project(nuevo_nombre)
                self._limpiar_campos()
                self._cargar_proyectos()
                self.project_selector.set_selected(nuevo_nombre)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _limpiar_campos(self):
        self.ruta_base_component.set("")
        self.directorio_principal_component.set("")
        self.archivos_text.delete()
        self.directorios_prohibidos_text.delete()
        self.archivos_prohibidos_text.delete()
        self.formatos_prohibidos_component.set("")
        self.prompt_text.delete()
        self.solicitud_text.delete()
        self.patron_component.set("")

    def _seleccionar_ruta_base(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.ruta_base_component.set(ruta)

    def _ejecutar_copia(self):
        proyecto_actual = self.project_selector.get_selected()
        if not proyecto_actual:
            messagebox.showerror("Error", "Selecciona o crea un proyecto primero")
            return

        config_data = {
            "ruta_base": self.ruta_base_component.get().strip(),
            "directorio_principal": self.directorio_principal_component.get().strip(),
            "archivos": self.archivos_text.get().strip(),
            "directorios_prohibidos": self.directorios_prohibidos_text.get().strip(),
            "archivos_prohibidos": self.archivos_prohibidos_text.get().strip(),
            "formatos_prohibidos": self.formatos_prohibidos_component.get().strip(),
            "prompt": self.prompt_text.get().strip(),
            "patron": self.patron_component.get().strip()
        }

        try:
            contenido, no_encontrados = self.file_processor.procesar_archivos(
                config_data,
                self.incluir_ruta_var.get()
            )

            if contenido:
                solicitud_text = self.solicitud_text.get().strip()
                if solicitud_text:
                    solicitud_text = f"SOLICITUD: {solicitud_text}"

                final_content = f"{config_data['prompt']}\n\n{solicitud_text}\n\n{contenido}"

                pyperclip.copy(final_content)
                self.config_handler.save_project_config(proyecto_actual, config_data)
                self.config_handler.set_current_project(proyecto_actual)

                mensaje = "Contenido copiado al portapapeles y configuración guardada"
                if no_encontrados:
                    mensaje += f"\n\nArchivos no encontrados:\n- " + "\n- ".join(no_encontrados)
                messagebox.showinfo("Operación Exitosa", mensaje)
            else:
                messagebox.showwarning("Sin Contenido", "No se encontró contenido válido para copiar")

        except Exception as e:
            messagebox.showerror("Error Crítico", f"Se produjo un error:\n{str(e)}")

    def _toggle_generador_archivos(self):
        if self.generador_activo_var.get():
            if not self._validar_configuracion_generador():
                self.generador_activo_var.set(False)
                return
            
            config = self._obtener_config_actual()
            base_path = config["ruta_base"]
            
            if self.file_generator and self.file_generator.is_alive():
                self.file_generator.stop()
            
            self.file_generator = FileGenerator(base_path)
            self.file_generator.start()
            messagebox.showinfo(
                "Generador activado", 
                f"Monitorizando portapapeles para crear archivos en:\n{base_path}"
            )
        else:
            if self.file_generator:
                self.file_generator.stop()
            messagebox.showinfo("Generador desactivado", "La monitorización se ha detenido")

    def _validar_configuracion_generador(self):
        config = self._obtener_config_actual()
        
        if not config["ruta_base"]:
            messagebox.showerror("Error", "Debes establecer una ruta base para el proyecto")
            return False
        
        if not os.path.exists(config["ruta_base"]):
            messagebox.showerror("Error", "La ruta base del proyecto no existe")
            return False
        
        return True

    def _obtener_config_actual(self):
        return {
            "ruta_base": self.ruta_base_component.get().strip(),
            "directorio_principal": self.directorio_principal_component.get().strip()
        }