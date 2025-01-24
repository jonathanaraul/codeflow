# app_gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pyperclip

class ApplicationGUI:
    def __init__(self, root, config_handler, file_processor):
        self.root = root
        self.config_handler = config_handler
        self.file_processor = file_processor
        self.current_project = None
        self.incluir_ruta_var = tk.BooleanVar(value=True)
        
        # Configuración de diseño
        self.colores = {
            'fondo': '#2D2D2D',
            'fondo_paneles': '#3A3A3A',
            'texto': '#FFFFFF',
            'acento': '#4A9CFF',
            'botones': '#5C5C5C',
            'hover': '#6B6B6B',
            'bordes': '#4A4A4A',
            'campo_texto': '#454545'
        }
        
        self.fuente_principal = ('Segoe UI', 10)
        self.fuente_titulos = ('Segoe UI', 11, 'bold')
        
        self._configurar_estilos()
        self._setup_ui()
        self._cargar_proyectos()

    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuración base
        style.configure('.', 
                        background=self.colores['fondo'],
                        foreground=self.colores['texto'],
                        font=self.fuente_principal,
                        borderwidth=0)
        
        # Componentes específicos
        style.configure('TFrame', background=self.colores['fondo_paneles'])
        style.configure('TLabel', background=self.colores['fondo_paneles'], font=self.fuente_titulos)
        style.configure('TEntry', 
                        fieldbackground=self.colores['campo_texto'],
                        foreground=self.colores['texto'],
                        bordercolor=self.colores['bordes'],
                        relief='flat')
        
        style.configure('TButton', 
                        background=self.colores['botones'],
                        borderwidth=1,
                        relief='flat',
                        font=self.fuente_principal)
        style.map('TButton',
                  background=[('active', self.colores['hover']), ('!disabled', self.colores['botones'])],
                  relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
        
        style.configure('TCheckbutton', 
                        background=self.colores['fondo_paneles'],
                        indicatormargin=5)
        
        style.configure('TCombobox',
                        fieldbackground=self.colores['campo_texto'],
                        arrowsize=12,
                        relief='flat')
        style.map('TCombobox',
                  fieldbackground=[('readonly', self.colores['campo_texto'])],
                  selectbackground=[('readonly', self.colores['acento'])])
        
        style.configure('Vertical.TScrollbar',
                        background=self.colores['botones'],
                        troughcolor=self.colores['fondo'],
                        bordercolor=self.colores['bordes'],
                        arrowcolor=self.colores['texto'],
                        gripcount=0)

    def _setup_ui(self):
        self.root.title("Gestor de Proyectos - Copiador Profesional")
        self.root.state('zoomed')
        self.root.configure(bg=self.colores['fondo'])
        self._crear_widgets()
        self._configurar_layout()

    def _crear_widgets(self):
        # Contenedor principal
        self.main_frame = ttk.Frame(self.root, style='TFrame', padding=10)
        self.left_panel = ttk.Frame(self.main_frame, style='TFrame', padding=15)
        self.right_panel = ttk.Frame(self.main_frame, style='TFrame', padding=15)

        # Panel derecho - Controles principales
        self.project_frame = ttk.Frame(self.right_panel, style='TFrame')
        self.project_selector = ttk.Combobox(
            self.project_frame, 
            state="readonly",
            style='TCombobox',
            height=25,
            font=self.fuente_principal
        )
        self.btn_nuevo_proyecto = ttk.Button(
            self.project_frame, 
            text="➕ Nuevo Proyecto", 
            command=self._nuevo_proyecto,
            style='TButton'
        )
        
        # Campos de entrada
        self.ruta_base_entry = ttk.Entry(
            self.right_panel, 
            width=60, 
            style='TEntry',
            font=self.fuente_principal
        )
        
        # Áreas de texto
        def crear_textarea(parent, height):
            return tk.Text(
                parent,
                width=70,
                height=height,
                bg=self.colores['campo_texto'],
                fg=self.colores['texto'],
                insertbackground=self.colores['texto'],
                relief='flat',
                font=self.fuente_principal,
                padx=8,
                pady=8,
                wrap=tk.WORD
            )
        
        self.prompt_textarea = crear_textarea(self.right_panel, 6)
        self.solicitud_textarea = crear_textarea(self.right_panel, 6)
        
        # Panel izquierdo - Configuraciones
        self.directorio_principal_entry = ttk.Entry(
            self.left_panel, 
            width=60, 
            style='TEntry'
        )

        # Nuevo campo Patrón
        self.patron_entry = ttk.Entry(
            self.left_panel,
            width=60,
            style='TEntry'
        )
        
        self.archivos_textarea = crear_textarea(self.left_panel, 4)
        self.directorios_prohibidos_textarea = crear_textarea(self.left_panel, 4)
        self.archivos_prohibidos_textarea = crear_textarea(self.left_panel, 4)
        
        # Convertir formatos_prohibidos a Entry en lugar de Text
        self.formatos_prohibidos_entry = ttk.Entry(
            self.left_panel,
            width=60,
            style='TEntry'
        )
        
        # Botones y controles
        self.checkbutton = ttk.Checkbutton(
            self.right_panel,
            text="Incluir rutas y nombres de archivo",
            variable=self.incluir_ruta_var,
            style='TCheckbutton'
        )
        
        self.btn_seleccionar = ttk.Button(
            self.right_panel, 
            text="📂 Seleccionar Ruta", 
            command=self._seleccionar_ruta_base,
            style='TButton'
        )
        
        self.btn_copiar = ttk.Button(
            self.right_panel, 
            text="⎘ Copiar y Guardar", 
            command=self._ejecutar_copia,
            style='TButton'
        )
        
        # Scrollbars personalizadas para las áreas de texto
        def agregar_scrollbar(text_widget):
            scroll = ttk.Scrollbar(text_widget, style='Vertical.TScrollbar')
            scroll.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scroll.set)
            scroll.config(command=text_widget.yview)
        
        for area in [
            self.prompt_textarea, 
            self.solicitud_textarea,
            self.archivos_textarea, 
            self.directorios_prohibidos_textarea,
            self.archivos_prohibidos_textarea
        ]:
            agregar_scrollbar(area)

    def _configurar_layout(self):
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configuración de paneles
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.left_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # Panel derecho
        ttk.Label(self.right_panel, text="PROYECTO ACTUAL:").pack(pady=(0, 10), anchor=tk.W)
        self.project_frame.pack(fill=tk.X, pady=5)
        self.project_selector.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        self.btn_nuevo_proyecto.pack(side=tk.RIGHT)
        
        ttk.Label(self.right_panel, text="RUTA BASE DEL PROYECTO:").pack(pady=(15, 5), anchor=tk.W)
        self.ruta_base_entry.pack(fill=tk.X, pady=5)
        self.btn_seleccionar.pack(pady=10, ipadx=10)
        
        ttk.Label(self.right_panel, text="PROMPT DE CONTEXTO:").pack(pady=(15, 5), anchor=tk.W)
        self.prompt_textarea.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.right_panel, text="SOLICITUD ACTUAL:").pack(pady=(15, 5), anchor=tk.W)
        self.solicitud_textarea.pack(fill=tk.BOTH, expand=True)
        
        self.checkbutton.pack(pady=15, anchor=tk.W)
        self.btn_copiar.pack(pady=20, ipadx=20, ipady=8)

        # Panel izquierdo
        ttk.Label(self.left_panel, text="CONFIGURACIÓN AVANZADA").pack(pady=(0, 15), anchor=tk.W)
        
        ttk.Label(self.left_panel, text="Directorio Principal (opcional):").pack(pady=(0, 5), anchor=tk.W)
        self.directorio_principal_entry.pack(fill=tk.X, pady=5)

        ttk.Label(self.left_panel, text="Patrón (opcional):").pack(pady=(15, 5), anchor=tk.W)
        self.patron_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.left_panel, text="Archivos Específicos:").pack(pady=(15, 5), anchor=tk.W)
        self.archivos_textarea.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.left_panel, text="Directorios Prohibidos:").pack(pady=(15, 5), anchor=tk.W)
        self.directorios_prohibidos_textarea.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.left_panel, text="Archivos Prohibidos:").pack(pady=(15, 5), anchor=tk.W)
        self.archivos_prohibidos_textarea.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.left_panel, text="Formatos Prohibidos:").pack(pady=(15, 5), anchor=tk.W)
        self.formatos_prohibidos_entry.pack(fill=tk.X, pady=5)

    def _cargar_proyectos(self):
        proyectos = self.config_handler.get_projects()
        self.project_selector["values"] = proyectos
        current = self.config_handler.get_current_project()
        if current:
            self.project_selector.set(current)
            self._cargar_configuracion_proyecto(current)
        
        self.project_selector.bind(
            "<<ComboboxSelected>>", 
            lambda e: self._cargar_configuracion_proyecto(self.project_selector.get())
        )

    def _cargar_configuracion_proyecto(self, proyecto):
        config = self.config_handler.get_project_config(proyecto)
        if not config:
            return
        
        self.ruta_base_entry.delete(0, tk.END)
        self.ruta_base_entry.insert(0, config["ruta_base"])
        
        self.directorio_principal_entry.delete(0, tk.END)
        self.directorio_principal_entry.insert(0, config["directorio_principal"])
        
        self.archivos_textarea.delete("1.0", tk.END)
        self.archivos_textarea.insert(tk.END, config["archivos"])
        
        self.directorios_prohibidos_textarea.delete("1.0", tk.END)
        self.directorios_prohibidos_textarea.insert(tk.END, config["directorios_prohibidos"])
        
        self.archivos_prohibidos_textarea.delete("1.0", tk.END)
        self.archivos_prohibidos_textarea.insert(tk.END, config["archivos_prohibidos"])
        
        self.formatos_prohibidos_entry.delete(0, tk.END)
        self.formatos_prohibidos_entry.insert(0, config.get("formatos_prohibidos", ""))

        self.prompt_textarea.delete("1.0", tk.END)
        self.prompt_textarea.insert(tk.END, config.get("prompt", ""))

        self.patron_entry.delete(0, tk.END)
        self.patron_entry.insert(0, config.get("patron", ""))

        self.solicitud_textarea.delete("1.0", tk.END)

    def _nuevo_proyecto(self):
        nuevo_nombre = self._pedir_nombre_proyecto()
        if nuevo_nombre:
            try:
                self.config_handler.create_new_project(nuevo_nombre)
                self.config_handler.set_current_project(nuevo_nombre)
                self._limpiar_campos()
                self._cargar_proyectos()
                self.project_selector.set(nuevo_nombre)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _pedir_nombre_proyecto(self):
        return simpledialog.askstring(
            "Nuevo Proyecto", 
            "Nombre del nuevo proyecto:",
            parent=self.root,
            font=self.fuente_principal
        )

    def _limpiar_campos(self):
        self.ruta_base_entry.delete(0, tk.END)
        self.directorio_principal_entry.delete(0, tk.END)
        self.archivos_textarea.delete("1.0", tk.END)
        self.directorios_prohibidos_textarea.delete("1.0", tk.END)
        self.archivos_prohibidos_textarea.delete("1.0", tk.END)
        self.formatos_prohibidos_entry.delete(0, tk.END)
        self.prompt_textarea.delete("1.0", tk.END)
        self.solicitud_textarea.delete("1.0", tk.END)
        self.patron_entry.delete(0, tk.END)

    def _seleccionar_ruta_base(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.ruta_base_entry.delete(0, tk.END)
            self.ruta_base_entry.insert(0, ruta)

    def _ejecutar_copia(self):
        proyecto_actual = self.project_selector.get()
        if not proyecto_actual:
            messagebox.showerror("Error", "Selecciona o crea un proyecto primero")
            return

        config_data = {
            "ruta_base": self.ruta_base_entry.get().strip(),
            "directorio_principal": self.directorio_principal_entry.get().strip(),
            "archivos": self.archivos_textarea.get("1.0", tk.END).strip(),
            "directorios_prohibidos": self.directorios_prohibidos_textarea.get("1.0", tk.END).strip(),
            "archivos_prohibidos": self.archivos_prohibidos_textarea.get("1.0", tk.END).strip(),
            "formatos_prohibidos": self.formatos_prohibidos_entry.get().strip(),
            "prompt": self.prompt_textarea.get("1.0", tk.END).strip(),
            "patron": self.patron_entry.get().strip()
        }

        try:
            contenido, no_encontrados = self.file_processor.procesar_archivos(
                config_data, 
                self.incluir_ruta_var.get()
            )
            
            if contenido:
                solicitud_text = self.solicitud_textarea.get("1.0", tk.END).strip()
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
