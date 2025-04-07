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
        self.solo_consulta_var = tk.BooleanVar(value=False) # <--- NUEVA VARIABLE
        self.file_generator = None

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # Ajuste para evitar que la ventana ocupe toda la altura (considerando barra de tareas)
        adjusted_height = screen_height - 80 # Un poco más de margen
        self.root.geometry(f"{screen_width}x{adjusted_height}+0+0")
        self.root.title("Code Context Copier & File Generator") # Añadir un título

        self.style_manager = StyleManager()
        self._setup_main_frames()
        self._create_right_panel_widgets() # Crear panel derecho primero
        self._create_left_panel_widgets() # Luego panel izquierdo
        self._cargar_proyectos() # Cargar proyectos al final

        # Configurar evento de cierre
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)


    def _setup_main_frames(self):
        self.main_frame = ttk.Frame(self.root, style='TFrame', padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Dar más peso al panel derecho si se desea que sea más grande
        self.main_frame.grid_columnconfigure(0, weight=2) # Panel derecho
        self.main_frame.grid_columnconfigure(1, weight=1) # Panel izquierdo
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.right_panel = ttk.Frame(self.main_frame, style='TFrame', padding=15)
        # Usar grid para mejor control del tamaño relativo
        self.right_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        self.left_panel = ttk.Frame(self.main_frame, style='TFrame', padding=15)
        # Usar grid para mejor control del tamaño relativo
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
        # Bindear evento de selección
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
            "📂 Seleccionar", # Texto más corto
            self._seleccionar_ruta_base
        )
        self.btn_seleccionar.pack(side=tk.RIGHT)

        # --- Sección Prompt ---
        ttk.Label(self.right_panel, text="PROMPT DE CONTEXTO:").pack(pady=(15, 5), anchor=tk.W)
        self.prompt_text = ScrolledText(self.right_panel, self.style_manager, height=6) # Ajustar altura si es necesario
        self.prompt_text.frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # --- Sección Solicitud ---
        ttk.Label(self.right_panel, text="SOLICITUD ACTUAL:").pack(pady=(5, 5), anchor=tk.W)
        self.solicitud_text = ScrolledText(self.right_panel, self.style_manager, height=6) # Ajustar altura si es necesario
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

        # --- Cambio: Añadir Checkbox "Solo consulta" ---
        ttk.Checkbutton(
            options_frame,
            text="Solo consulta",
            variable=self.solo_consulta_var, # Usar la nueva variable
            style='TCheckbutton'
        ).pack(side=tk.LEFT, padx=(0, 15), anchor=tk.W)
        # --- Fin Cambio ---

        ttk.Checkbutton(
            options_frame,
            text="Generador de archivos",
            variable=self.generador_activo_var,
            command=self._toggle_generador_archivos,
            style='TCheckbutton'
        ).pack(side=tk.LEFT, anchor=tk.W)


        # --- Sección Botones de Acción ---
        action_button_frame = ttk.Frame(self.right_panel, style='TFrame')
        action_button_frame.pack(fill=tk.X, pady=(15, 0)) # Espacio arriba

        self.btn_copiar = CustomButton(
            action_button_frame,
            self.style_manager,
            "⎘ Copiar y Guardar",
            self._ejecutar_copia
        )
        # Usar grid dentro del frame para centrar o alinear mejor si hay más botones
        action_button_frame.grid_columnconfigure(0, weight=1)
        action_button_frame.grid_columnconfigure(1, weight=1)
        action_button_frame.grid_columnconfigure(2, weight=1)

        self.btn_copiar.button.grid(row=0, column=1, pady=10, padx=5, ipady=5, sticky="ew") # Centrado horizontal

        # Botón Limpiar Solicitud
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
            "Directorio Principal (relativo a Ruta Base, opcional):" # Aclarar relatividad
        )
        self.directorio_principal_component.frame.pack(fill=tk.X, pady=5)

        self.patron_component = LabeledEntry(
            self.left_panel,
            self.style_manager,
            "Patrón de Archivo (opcional, separar con comas para OR):" # Aclarar uso de comas
        )
        self.patron_component.frame.pack(fill=tk.X, pady=5)

        # Usar Frames para agrupar Labels y Text Areas
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
            "Formatos Prohibidos (ej: .log, .tmp, separados por coma):" # Añadir ejemplo
        )
        self.formatos_prohibidos_component.frame.pack(fill=tk.X, pady=5)


    def _cargar_proyectos(self):
        """Carga la lista de proyectos (ordenada por uso) y selecciona el actual."""
        try:
             proyectos = self.config_handler.get_projects() # Ya viene ordenada
             self.project_selector.set_projects(proyectos)
             current = self.config_handler.get_current_project()
             if current and current in proyectos: # Verificar que el actual aún existe
                 self.project_selector.set_selected(current)
                 self._cargar_configuracion_proyecto(current, update_timestamp=False) # Evitar doble actualización de timestamp al inicio
             elif proyectos: # Si no hay actual o no existe, seleccionar el primero (más reciente)
                  first_project = proyectos[0]
                  self.project_selector.set_selected(first_project)
                  self._cargar_configuracion_proyecto(first_project, update_timestamp=False) # Evitar doble actualización
             else:
                  self._limpiar_campos() # No hay proyectos, limpiar todo
        except Exception as e:
             messagebox.showerror("Error Cargando Proyectos", f"No se pudieron cargar los proyectos: {str(e)}")
             self._limpiar_campos()

    def _cargar_configuracion_proyecto(self, proyecto, update_timestamp=True):
        """Carga la configuración del proyecto seleccionado en la GUI."""
        if not proyecto:
             return

        # Detener generador si estaba activo para otro proyecto
        if self.file_generator and self.file_generator.is_alive():
            self.generador_activo_var.set(False) # Desmarcar checkbox
            self._toggle_generador_archivos() # Llamar a la función para detenerlo limpiamente

        try:
            config = self.config_handler.get_project_config(proyecto)
            if not config:
                messagebox.showerror("Error", f"No se encontró la configuración para '{proyecto}'")
                return

            # Cargar datos en la GUI
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
            self.patron_component.set(config.get("patron", ""))
            self.solo_archivos_especificos_var.set(config.get("solo_archivos_especificos", False))
            self.solicitud_text.delete() # Limpiar solicitud anterior al cambiar de proyecto
            self.solo_consulta_var.set(False) # Resetear "Solo consulta" al cambiar de proyecto

            # Actualizar timestamp al seleccionar
            if update_timestamp:
                 self.config_handler.set_current_project(proyecto)

            self.current_project = proyecto # Actualizar variable interna

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
             nuevo_nombre = nuevo_nombre.strip() # Limpiar espacios
             try:
                 self.config_handler.create_new_project(nuevo_nombre)
                 self._cargar_proyectos() # Recargar la lista (ahora ordenada)
                 if nuevo_nombre in self.project_selector.combobox["values"]:
                      self.project_selector.set_selected(nuevo_nombre)
                      self._cargar_configuracion_proyecto(nuevo_nombre, update_timestamp=True) # Cargar y marcar como usado
                 else:
                      messagebox.showwarning("Advertencia", f"Proyecto '{nuevo_nombre}' creado pero no encontrado en la lista.")

             except ValueError as e: # Capturar error específico de nombre duplicado/vacío
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
        self.patron_component.set("")
        self.solo_archivos_especificos_var.set(False)
        self.incluir_ruta_var.set(True) # Valor por defecto
        self.solo_consulta_var.set(False) # Resetear
        if limpiar_proyecto_actual:
             self.project_selector.set_selected("") # Deseleccionar combobox
             self.current_project = None

    def _limpiar_solicitud(self):
        """Borra el contenido del área de texto de la solicitud actual."""
        self.solicitud_text.delete()
        print("[GUI] Solicitud actual limpiada.") # Log opcional

    def _seleccionar_ruta_base(self):
        """Abre diálogo para seleccionar directorio de ruta base."""
        ruta_inicial = self.ruta_base_component.get() or os.path.expanduser("~") # Usar ruta actual o home
        ruta = filedialog.askdirectory(initialdir=ruta_inicial, title="Selecciona la Ruta Base del Proyecto")
        if ruta:
            self.ruta_base_component.set(os.path.normpath(ruta)) # Normalizar ruta

    def _ejecutar_copia(self):
        """Recopila configuración, procesa archivos, copia al portapapeles y guarda."""
        proyecto_actual = self.project_selector.get_selected()
        if not proyecto_actual:
            messagebox.showerror("Error", "Selecciona o crea un proyecto primero.")
            return

        # Validar Ruta Base antes de continuar
        ruta_base = self.ruta_base_component.get().strip()
        if not ruta_base or not os.path.isdir(ruta_base):
             messagebox.showerror("Error", "La Ruta Base del Proyecto no es válida o no existe.")
             return

        config_data = {
            "ruta_base": ruta_base,
            "directorio_principal": self.directorio_principal_component.get().strip(),
            # Limpiar y asegurar formato de lista para archivos específicos
            "archivos": ",".join([a.strip() for a in self.archivos_text.get().split(',') if a.strip()]),
             "directorios_prohibidos": self.directorios_prohibidos_text.get().strip(),
             "archivos_prohibidos": self.archivos_prohibidos_text.get().strip(),
             "formatos_prohibidos": self.formatos_prohibidos_component.get().strip(),
             "prompt": self.prompt_text.get().strip(),
             "patron": self.patron_component.get().strip(),
             "solo_archivos_especificos": self.solo_archivos_especificos_var.get()
        }

        try:
            contenido, no_encontrados = self.file_processor.procesar_archivos(
                config_data,
                self.incluir_ruta_var.get()
            )

            if not contenido and not no_encontrados:
                # Si no hay contenido y tampoco archivos no encontrados (probablemente por filtros muy estrictos)
                messagebox.showwarning("Sin Contenido", "No se encontró ningún archivo que coincidiera con los filtros aplicados.")
                return # No copiar ni guardar si no hubo nada que procesar

            # Solo copiar y guardar si se generó algún contenido (aunque haya archivos no encontrados)
            if contenido:
                prompt_text = config_data['prompt']
                solicitud_text = self.solicitud_text.get().strip()

                # Construir el texto final
                partes_finales = []

                # --- Cambio: Incluir prompt solo si "Solo consulta" NO está marcado ---
                if prompt_text and not self.solo_consulta_var.get():
                    partes_finales.append(prompt_text)
                # --- Fin Cambio ---

                if solicitud_text:
                    # Añadir prefijo claro a la solicitud
                    partes_finales.append(f"--- SOLICITUD ---\n{solicitud_text}")

                # Añadir el contenido de los archivos
                partes_finales.append(f"--- CONTEXTO ARCHIVOS ({'Rutas Incluidas' if self.incluir_ruta_var.get() else 'Solo Nombres'}) ---{contenido}")

                final_content = "\n\n".join(partes_finales).strip() # Unir con doble salto de línea

                try:
                     pyperclip.copy(final_content)
                     # Guardar la configuración ANTES de mostrar el mensaje de éxito
                     self.config_handler.save_project_config(proyecto_actual, config_data)
                     # La llamada a save_project_config ya actualiza el timestamp via set_current_project

                     mensaje = "Contenido copiado y configuración guardada."
                     if no_encontrados:
                         mensaje += "\n\nArchivos específicos no encontrados:\n- " + "\n- ".join(no_encontrados)
                     messagebox.showinfo("Operación Exitosa", mensaje)

                except pyperclip.PyperclipException as clip_error:
                     messagebox.showerror("Error Copiando", f"No se pudo copiar al portapapeles: {clip_error}")
                except Exception as save_error:
                     messagebox.showerror("Error Guardando", f"Contenido copiado, pero hubo un error al guardar la configuración: {save_error}")

            elif no_encontrados:
                # Si solo hubo archivos no encontrados, informar sin copiar/guardar
                messagebox.showwarning("Archivos No Encontrados", "No se generó contenido.\nArchivos específicos no encontrados:\n- " + "\n- ".join(no_encontrados))

        except Exception as e:
            messagebox.showerror("Error Crítico en Procesamiento", f"Se produjo un error inesperado al procesar los archivos:\n{str(e)}")


    def _toggle_generador_archivos(self):
        """Activa o desactiva el monitor de portapapeles para generar archivos."""
        if self.generador_activo_var.get(): # Si se acaba de marcar para activar
            if not self._validar_configuracion_generador():
                self.generador_activo_var.set(False) # Desmarcar si la validación falla
                return

            config = self._obtener_config_actual()
            base_path = config["ruta_base"]

            # Detener instancia anterior si existe y está viva (por si acaso)
            if self.file_generator and self.file_generator.is_alive():
                self.file_generator.stop()
                self.file_generator.join(timeout=1) # Esperar un poco a que termine

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

        else: # Si se acaba de desmarcar para desactivar
            if self.file_generator and self.file_generator.is_alive():
                self.file_generator.stop()
                self.file_generator.join(timeout=1) # Esperar que termine el hilo
                messagebox.showinfo("Generador Desactivado", "La monitorización del portapapeles se ha detenido.")
            elif self.file_generator:
                 print("[Generador] Ya estaba detenido.") # Log interno
            else:
                 print("[Generador] No estaba activo.")

            self.file_generator = None # Limpiar referencia


    def _validar_configuracion_generador(self):
        """Valida que la ruta base sea válida para el generador."""
        config = self._obtener_config_actual()
        ruta_base = config["ruta_base"]

        if not ruta_base:
            messagebox.showerror("Error: Ruta Base Requerida", "Debes establecer una Ruta Base válida para el proyecto antes de activar el generador.")
            return False

        if not os.path.isdir(ruta_base): # Comprobar si es un directorio válido
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
                 self.file_generator.join(timeout=1) # Dar tiempo a detenerse
                 self.root.destroy()
             else:
                 return # No cerrar si el usuario cancela
         else:
             if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir?"):
                 self.root.destroy()

# --- Fin de la clase MainWindow ---