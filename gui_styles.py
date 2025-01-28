# gui_styles.py
import tkinter as tk
from tkinter import ttk

class StyleManager:
    def __init__(self):
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

        self._configurar_tema()
        self._configurar_estilos_basicos()
        self._configurar_componentes()

    def _configurar_tema(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

    def _configurar_estilos_basicos(self):
        self.style.configure(
            '.',
            background=self.colores['fondo'],
            foreground=self.colores['texto'],
            font=self.fuente_principal,
            borderwidth=0
        )

    def _configurar_componentes(self):
        # Frame
        self.style.configure('TFrame', background=self.colores['fondo_paneles'])

        # Labels
        self.style.configure(
            'TLabel',
            background=self.colores['fondo_paneles'],
            font=self.fuente_titulos
        )

        # Entries
        self.style.configure(
            'TEntry',
            fieldbackground=self.colores['campo_texto'],
            foreground=self.colores['texto'],
            bordercolor=self.colores['bordes'],
            relief='flat'
        )

        # Buttons
        self.style.configure(
            'TButton',
            background=self.colores['botones'],
            borderwidth=1,
            relief='flat',
            font=self.fuente_principal
        )
        self.style.map(
            'TButton',
            background=[
                ('active', self.colores['hover']),
                ('!disabled', self.colores['botones'])
            ],
            relief=[
                ('pressed', 'sunken'),
                ('!pressed', 'flat')
            ]
        )

        # Checkbuttons
        self.style.configure(
            'TCheckbutton',
            background=self.colores['fondo_paneles'],
            indicatormargin=5
        )

        # Combobox
        self.style.configure(
            'TCombobox',
            fieldbackground=self.colores['campo_texto'],
            arrowsize=12,
            relief='flat'
        )
        self.style.map(
            'TCombobox',
            fieldbackground=[('readonly', self.colores['campo_texto'])],
            selectbackground=[('readonly', self.colores['acento'])]
        )

        # Scrollbar
        self.style.configure(
            'Vertical.TScrollbar',
            background=self.colores['botones'],
            troughcolor=self.colores['fondo'],
            bordercolor=self.colores['bordes'],
            arrowcolor=self.colores['texto'],
            gripcount=0
        )

    def get_text_widget_style(self):
        return {
            'bg': self.colores['campo_texto'],
            'fg': self.colores['texto'],
            'insertbackground': self.colores['texto'],
            'relief': 'flat',
            'font': self.fuente_principal,
            'padx': 8,
            'pady': 8,
            'wrap': tk.WORD
        }