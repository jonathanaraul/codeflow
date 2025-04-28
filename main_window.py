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
import time # Necesario si usamos time.sleep, aunque no directamente aquí

class MainWindow:
    def __init__(self, root, config_handler, file_processor):
        self.root = root
        self.config_handler = config_handler
        self.file_processor = file_processor
        self.current_project = None
        self.incluir_ruta_var = tk.BooleanVar(value=True)
        self.solo_archivos_especificos_var = tk.BooleanVar(value=False)
        self.generador_activo_var = tk.BooleanVar(value=False)
        self.solo_consulta_var = tk.BooleanVar(value=False) # Mantenido como estaba
        self.file_generator = None

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        adjusted_height = screen_height - 80
        self.root.geometry(f"{screen_width}x{adjusted_height}+0+0")
        self.root.title("Code Context Copier & File Generator")

        self.style_manager = StyleManager()
        self._setup_main_frames()
        self._create_right_panel_widgets()
        self._create_left_panel_widgets()
        self._cargar_proyectos()

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)


    def _setup_main_frames(self):
        self.main_frame = ttk.Frame(self.root, style='TFrame', padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.main_frame.grid_columnconfigure(0, weight=2)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.right_panel = ttk.Frame(self.main_frame, style='TFrame', padding=15)
        self.right_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        self.left_panel = ttk.Frame(self.main_frame, style='TFrame', padding=15)
        self.left_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))


    def _create_right_panel_widgets(self):
        # --- Sección Proyecto ---
        project_frame = ttk.Frame(self.right_panel, style='TFrame')
        project_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(project_frame, text="PROYECTO ACTUAL:").pack(side=tk.TOP, anchor=tk.W)
        self.project_selector = ProjectSelector(
            project_frame,
            self.style_manager,
            [],
            self._nuevo_proyecto
        )
        self.project_selector.frame.pack(fill=tk.X, pady=(5, 0))
        self.project_selector.combobox.bind(
            "<<ComboboxSelected>>",
            lambda e: self._cargar_configuracion_proyecto(
                self.project_selector.get_selected()
            )
        )

        # --- Sección Ruta Base ---
        ruta_frame = ttk.Frame(self.right_panel, style='TFrame')
        ruta_frame.pack(fill=tk.X, pady=5)
        self.ruta_base_component = LabeledEntry(
            ruta_frame,
            self.style_manager,
            "RUTA BASE DEL PROYECTO:"
        )
        self.ruta_base_component.frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.btn_seleccionar = CustomButton(
            ruta_frame,
            self.style_manager,
            "📂 Seleccionar",
            self._seleccionar_ruta_base
        )
        self.btn_seleccionar.pack(side=tk.RIGHT)

        # --- Sección Prompt ---
        ttk.Label(self.right_panel, text="PROMPT DE CONTEXTO:").pack(pady=(15, 5), anchor=tk.W)
        self.prompt_text = ScrolledText(self.right_panel, self.style_manager, height=6)
        self.prompt_text.frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # --- Sección Solicitud ---
        ttk.Label(self.right_panel, text="SOLICITUD ACTUAL:").pack(pady=(5, 5), anchor=tk.W)
        self.solicitud_text = ScrolledText(self.right_panel, self.style_manager, height=6)
        self.solicitud_text.frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # --- Sección Opciones Checkbox ---
        options_frame = ttk.Frame(self.right_panel, style='TFrame')
        options_frame.pack(fill=tk.X, pady=10)

        ttk.Checkbutton(
            options_frame,
            text="Incluir rutas/nombres archivo",
            variable=self.incluir_ruta_var,
            style='TCheckbutton'
        ).pack(side=tk.LEFT, padx=(0, 15), anchor=tk.W)

        ttk.Checkbutton(
            options_frame,
            text="Solo archivos específicos",
            variable=self.solo_archivos_especificos_var,
            style='TCheckbutton'
        ).pack(side=tk.LEFT, padx=(0, 15), anchor=tk.W)

        ttk.Checkbutton(
            options_frame,
            text="Solo consulta",
            variable=self.solo_consulta_var, # Mantenido
            style='TCheckbutton'
        ).pack(side=tk.LEFT, padx=(0, 15), anchor=tk.W)

        ttk.Checkbutton(
            options_frame,
            text="Generador de archivos",
            variable=self.generador_activo_var,
            command=self._toggle_generador_archivos,
            style='TCheckbutton'
        ).pack(side=tk.LEFT, anchor=tk.W)


        # --- Sección Botones de Acción ---
        action_button_frame = ttk.Frame(self.right_panel, style='TFrame')
        action_button_frame.pack(fill=tk.X, pady=(15, 0))

        action_button_frame.grid_columnconfigure(0, weight=1)
        action_button_frame.grid_columnconfigure(1, weight=1)
        action_button_frame.grid_columnconfigure(2, weight=1)

        self.btn_copiar = CustomButton(
            action_button_frame,
            self.style_manager,
            "⎘ Copiar y Guardar",
            self._ejecutar_copia
        )
        self.btn_copiar.button.grid(row=0, column=1, pady=10, padx=5, ipady=5, sticky="ew")

        self.btn_limpiar_solicitud = CustomButton(
             action_button_frame,
             self.style_manager,
             "🧹 Limpiar Solicitud",
             self._limpiar_solicitud
        )
        self.btn_limpiar_solicitud.button.grid(row=0, column=2, pady=10, padx=5, ipady=5, sticky="ew")


    def _create_left_panel_widgets(self):
        ttk.Label(self.left_panel, text="CONFIGURACIÓN AVANZADA").pack(pady=(0, 15), anchor=tk.W)

        self.directorio_principal_component = LabeledEntry(
            self.left_panel,
            self.style_manager,
            "Directorio Principal (relativo a Ruta Base, opcional):"
        )
        self.directorio_principal_component.frame.pack(fill=tk.X, pady=5)

        # --- Cambio: Actualizar etiqueta del campo de patrones ---
        # Se mantiene el nombre de variable self.patron_component por simplicidad,
        # pero la etiqueta y la lógica de guardado/carga usarán "patrones".
        self.patron_component = LabeledEntry(
            self.left_panel,
            self.style_manager,
            "Patrones (+incluir, -excluir, separar con coma):" # <<< ETIQUETA ACTUALIZADA AQUÍ
        )
        self.patron_component.frame.pack(fill=tk.X, pady=5)
        # --- Fin Cambio ---

        archivos_frame = ttk.Frame(self.left_panel, style='TFrame')
        archivos_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 5))
        ttk.Label(archivos_frame, text="Archivos Específicos (uno por línea o separados por coma):").pack(anchor=tk.W)
        self.archivos_text = ScrolledText(archivos_frame, self.style_manager, height=4)
        self.archivos_text.frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        dir_prohibidos_frame = ttk.Frame(self.left_panel, style='TFrame')
        dir_prohibidos_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        ttk.Label(dir_prohibidos_frame, text="Directorios Prohibidos (separados por coma):").pack(anchor=tk.W)
        self.directorios_prohibidos_text = ScrolledText(dir_prohibidos_frame, self.style_manager, height=4)
        self.directorios_prohibidos_text.frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        arch_prohibidos_frame = ttk.Frame(self.left_panel, style='TFrame')
        arch_prohibidos_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        ttk.Label(arch_prohibidos_frame, text="Archivos Prohibidos (separados por coma):").pack(anchor=tk.W)
        self.archivos_prohibidos_text = ScrolledText(arch_prohibidos_frame, self.style_manager, height=4)
        self.archivos_prohibidos_text.frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.formatos_prohibidos_component = LabeledEntry(
            self.left_panel,
            self.style_manager,
            "Formatos Prohibidos (ej: .log, .tmp, separados por coma):"
        )
        self.formatos_prohibidos_component.frame.pack(fill=tk.X, pady=5)


    def _cargar_proyectos(self):
        """Carga la lista de proyectos (ordenada por uso) y selecciona el actual."""
        try:
            proyectos = self.config_handler.get_projects()
            self.project_selector.set_projects(proyectos)
            current = self.config_handler.get_current_project()
            if current and current in proyectos:
                self.project_selector.set_selected(current)
                self._cargar_configuracion_proyecto(current, update_timestamp=False)
            elif proyectos:
                first_project = proyectos[0]
                self.project_selector.set_selected(first_project)
                self._cargar_configuracion_proyecto(first_project, update_timestamp=False)
            else:
                self._limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error Cargando Proyectos", f"No se pudieron cargar los proyectos: {str(e)}")
            self._limpiar_campos()

    def _cargar_configuracion_proyecto(self, proyecto, update_timestamp=True):
        """Carga la configuración del proyecto seleccionado en la GUI."""
        if not proyecto:
            return

        if self.file_generator and self.file_generator.is_alive():
            self.generador_activo_var.set(False)
            self._toggle_generador_archivos()

        try:
            config = self.config_handler.get_project_config(proyecto)
            if not config:
                messagebox.showerror("Error", f"No se encontró la configuración para '{proyecto}'")
                return

            self.ruta_base_component.set(config.get("ruta_base", ""))
            self.directorio_principal_component.set(config.get("directorio_principal", ""))
            self.archivos_text.delete()
            self.archivos_text.insert(config.get("archivos", ""))
            self.directorios_prohibidos_text.delete()
            self.directorios_prohibidos_text.insert(config.get("directorios_prohibidos", ""))
            self.archivos_prohibidos_text.delete()
            self.archivos_prohibidos_text.insert(config.get("archivos_prohibidos", ""))
            self.formatos_prohibidos_component.set(config.get("formatos_prohibidos", ""))
            self.prompt_text.delete()
            self.prompt_text.insert(config.get("prompt", ""))
            # --- Cambio: Cargar desde la clave "patrones" ---
            self.patron_component.set(config.get("patrones", "")) # <<< LEER DESDE "patrones" AQUÍ
            # --- Fin Cambio ---
            self.solo_archivos_especificos_var.set(config.get("solo_archivos_especificos", False))
            self.solicitud_text.delete()
            self.solo_consulta_var.set(False)

            if update_timestamp:
                self.config_handler.set_current_project(proyecto)

            self.current_project = proyecto

        except Exception as e:
            messagebox.showerror("Error Cargando Configuración", f"Error al cargar '{proyecto}': {str(e)}")


    def _nuevo_proyecto(self):
        """Solicita nombre y crea un nuevo proyecto."""
        nuevo_nombre = simpledialog.askstring(
            "Nuevo Proyecto",
            "Nombre del nuevo proyecto:",
            parent=self.root
        )
        if nuevo_nombre and not nuevo_nombre.isspace():
            nuevo_nombre = nuevo_nombre.strip()
            try:
                self.config_handler.create_new_project(nuevo_nombre)
                self._cargar_proyectos()
                if nuevo_nombre in self.project_selector.combobox["values"]:
                    self.project_selector.set_selected(nuevo_nombre)
                    self._cargar_configuracion_proyecto(nuevo_nombre, update_timestamp=True)
                else:
                    messagebox.showwarning("Advertencia", f"Proyecto '{nuevo_nombre}' creado pero no encontrado en la lista.")

            except ValueError as e:
                messagebox.showerror("Error Creando Proyecto", str(e))
            except Exception as e:
                messagebox.showerror("Error Inesperado", f"No se pudo crear el proyecto: {str(e)}")


    def _limpiar_campos(self, limpiar_proyecto_actual=True):
        """Limpia todos los campos de configuración de la GUI."""
        self.ruta_base_component.set("")
        self.directorio_principal_component.set("")
        self.archivos_text.delete()
        self.directorios_prohibidos_text.delete()
        self.archivos_prohibidos_text.delete()
        self.formatos_prohibidos_component.set("")
        self.prompt_text.delete()
        self.solicitud_text.delete()
        self.patron_component.set("") # Limpiar campo de patrones
        self.solo_archivos_especificos_var.set(False)
        self.incluir_ruta_var.set(True)
        self.solo_consulta_var.set(False)
        if limpiar_proyecto_actual:
            self.project_selector.set_selected("")
            self.current_project = None

    def _limpiar_solicitud(self):
        """Borra el contenido del área de texto de la solicitud actual."""
        self.solicitud_text.delete()
        print("[GUI] Solicitud actual limpiada.")

    def _seleccionar_ruta_base(self):
        """Abre diálogo para seleccionar directorio de ruta base."""
        ruta_inicial = self.ruta_base_component.get() or os.path.expanduser("~")
        ruta = filedialog.askdirectory(initialdir=ruta_inicial, title="Selecciona la Ruta Base del Proyecto")
        if ruta:
            self.ruta_base_component.set(os.path.normpath(ruta))

    def _ejecutar_copia(self):
        """Recopila configuración, procesa archivos, copia al portapapeles y guarda."""
        proyecto_actual = self.project_selector.get_selected()
        if not proyecto_actual:
            messagebox.showerror("Error", "Selecciona o crea un proyecto primero.")
            return

        ruta_base = self.ruta_base_component.get().strip()
        if not ruta_base or not os.path.isdir(ruta_base):
            messagebox.showerror("Error", "La Ruta Base del Proyecto no es válida o no existe.")
            return

        # --- Cambio: Guardar usando la clave "patrones" ---
        config_data = {
            "ruta_base": ruta_base,
            "directorio_principal": self.directorio_principal_component.get().strip(),
            "archivos": ",".join([a.strip() for a in self.archivos_text.get().split(',') if a.strip()]),
            "directorios_prohibidos": self.directorios_prohibidos_text.get().strip(),
            "archivos_prohibidos": self.archivos_prohibidos_text.get().strip(),
            "formatos_prohibidos": self.formatos_prohibidos_component.get().strip(),
            "prompt": self.prompt_text.get().strip(),
            "patrones": self.patron_component.get().strip(), # <<< GUARDAR VALOR COMO "patrones" AQUÍ
            "solo_archivos_especificos": self.solo_archivos_especificos_var.get()
        }
        # --- Fin Cambio ---

        try:
            contenido, no_encontrados = self.file_processor.procesar_archivos(
                config_data,
                self.incluir_ruta_var.get()
            )

            if not contenido and not no_encontrados:
                messagebox.showwarning("Sin Contenido", "No se encontró ningún archivo que coincidiera con los filtros aplicados.")
                return

            if contenido:
                prompt_text = config_data['prompt']
                solicitud_text = self.solicitud_text.get().strip()

                partes_finales = []

                if prompt_text and not self.solo_consulta_var.get():
                    partes_finales.append(prompt_text)

                if solicitud_text:
                    partes_finales.append(f"--- SOLICITUD ---\n{solicitud_text}")

                partes_finales.append(f"--- CONTEXTO ARCHIVOS ({'Rutas Incluidas' if self.incluir_ruta_var.get() else 'Solo Nombres'}) ---{contenido}")

                final_content = "\n\n".join(partes_finales).strip()

                try:
                    pyperclip.copy(final_content)
                    self.config_handler.save_project_config(proyecto_actual, config_data)

                    mensaje = "Contenido copiado y configuración guardada."
                    if no_encontrados:
                        mensaje += "\n\nArchivos específicos no encontrados:\n- " + "\n- ".join(no_encontrados)
                    messagebox.showinfo("Operación Exitosa", mensaje)

                except pyperclip.PyperclipException as clip_error:
                    messagebox.showerror("Error Copiando", f"No se pudo copiar al portapapeles: {clip_error}")
                except Exception as save_error:
                    messagebox.showerror("Error Guardando", f"Contenido copiado, pero hubo un error al guardar la configuración: {save_error}")

            elif no_encontrados:
                messagebox.showwarning("Archivos No Encontrados", "No se generó contenido.\nArchivos específicos no encontrados:\n- " + "\n- ".join(no_encontrados))

        except Exception as e:
            messagebox.showerror("Error Crítico en Procesamiento", f"Se produjo un error inesperado al procesar los archivos:\n{str(e)}")


    def _toggle_generador_archivos(self):
        """Activa o desactiva el monitor de portapapeles para generar archivos."""
        if self.generador_activo_var.get():
            if not self._validar_configuracion_generador():
                self.generador_activo_var.set(False)
                return

            config = self._obtener_config_actual()
            base_path = config["ruta_base"]

            if self.file_generator and self.file_generator.is_alive():
                self.file_generator.stop()
                self.file_generator.join(timeout=1)

            try:
                self.file_generator = FileGenerator(base_path)
                self.file_generator.start()
                messagebox.showinfo(
                    "Generador Activado",
                    f"Monitorizando portapapeles para crear archivos en:\n{base_path}"
                )

            except Exception as e:
                messagebox.showerror("Error Iniciando Generador", f"No se pudo iniciar el generador: {str(e)}")
                self.generador_activo_var.set(False)

        else:
            if self.file_generator and self.file_generator.is_alive():
                self.file_generator.stop()
                self.file_generator.join(timeout=1)
                messagebox.showinfo("Generador Desactivado", "La monitorización del portapapeles se ha detenido.")
            elif self.file_generator:
                print("[Generador] Ya estaba detenido.")
            else:
                print("[Generador] No estaba activo.")

            self.file_generator = None


    def _validar_configuracion_generador(self):
        """Valida que la ruta base sea válida para el generador."""
        config = self._obtener_config_actual()
        ruta_base = config["ruta_base"]

        if not ruta_base:
            messagebox.showerror("Error: Ruta Base Requerida", "Debes establecer una Ruta Base válida para el proyecto antes de activar el generador.")
            return False

        if not os.path.isdir(ruta_base):
            messagebox.showerror("Error: Ruta Base Inválida", f"La Ruta Base especificada no existe o no es un directorio:\n{ruta_base}")
            return False

        return True

    def _obtener_config_actual(self):
        """Devuelve un diccionario con la configuración mínima actual de la GUI."""
        return {
            "ruta_base": self.ruta_base_component.get().strip(),
        }

    def _on_closing(self):
         """Maneja el evento de cierre de la ventana."""
         if self.file_generator and self.file_generator.is_alive():
             if messagebox.askyesno("Generador Activo", "El generador de archivos está activo. ¿Deseas detenerlo y salir?"):
                 self.file_generator.stop()
                 self.file_generator.join(timeout=1)
                 self.root.destroy()
             else:
                 return
         else:
             if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir?"):
                 self.root.destroy()

# --- Fin de la clase MainWindow ---