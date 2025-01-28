# gui_components.py
import tkinter as tk
from tkinter import ttk

class ScrolledText:
    """Componente de área de texto con scrollbar personalizado"""
    def __init__(self, parent, style_manager, height=6):
        self.frame = ttk.Frame(parent)
        self.style_manager = style_manager
        self.height = height

        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self):
        text_style = self.style_manager.get_text_widget_style()
        self.text_widget = tk.Text(
            self.frame,
            width=70,
            height=self.height,
            **text_style
        )

        self.scrollbar = ttk.Scrollbar(
            self.frame,
            style='Vertical.TScrollbar'
        )

    def _setup_layout(self):
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_widget.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_widget.yview)

    def get(self):
        return self.text_widget.get("1.0", tk.END)

    def delete(self):
        self.text_widget.delete("1.0", tk.END)

    def insert(self, content):
        self.text_widget.insert(tk.END, content)

class CustomButton:
    """Botón personalizado con estilo consistente"""
    def __init__(self, parent, style_manager, text, command):
        self.style_manager = style_manager
        self.button = ttk.Button(
            parent,
            text=text,
            command=command,
            style='TButton'
        )

    def pack(self, **kwargs):
        self.button.pack(**kwargs)

class LabeledEntry:
    """Campo de entrada con etiqueta integrada"""
    def __init__(self, parent, style_manager, label_text):
        self.frame = ttk.Frame(parent)
        self.style_manager = style_manager
        self.label_text = label_text

        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self):
        self.label = ttk.Label(self.frame, text=self.label_text)
        self.entry = ttk.Entry(
            self.frame,
            width=60,
            style='TEntry'
        )

    def _setup_layout(self):
        self.label.pack(pady=(0, 5), anchor=tk.W)
        self.entry.pack(fill=tk.X, pady=5)

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)

class ProjectSelector:
    """Componente combinado de selector de proyectos y botón de nuevo"""
    def __init__(self, parent, style_manager, proyectos, command):
        self.frame = ttk.Frame(parent)
        self.style_manager = style_manager
        self.proyectos = proyectos
        self.command = command

        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self):
        self.combobox = ttk.Combobox(
            self.frame,
            state="readonly",
            style='TCombobox',
            height=25
        )
        self.combobox["values"] = self.proyectos

        self.new_btn = ttk.Button(
            self.frame,
            text="➕ Nuevo Proyecto",
            command=self.command,
            style='TButton'
        )

    def _setup_layout(self):
        self.combobox.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        self.new_btn.pack(side=tk.RIGHT)

    def get_selected(self):
        return self.combobox.get()

    def set_projects(self, proyectos):
        self.combobox["values"] = proyectos

    def set_selected(self, project):
        self.combobox.set(project)