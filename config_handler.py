# config_handler.py
import json
import os
import time # Importado para manejar timestamps

class ConfigHandler:
    CONFIG_FILE = "config.json"
    SCHEMA_FILE = "config_schema.json" # Asumiendo que podrías tener un esquema

    DEFAULT_CONFIG = {
        "current_project": None,
        "projects": {},
        "project_metadata": {} # Nuevo: Para almacenar metadatos como last_used
    }

    PROJECT_DEFAULTS = {
        "ruta_base": "",
        "directorio_principal": "",
        "archivos": "",
        "directorios_prohibidos": "node_modules,.git,.vscode,dist,build",
        "archivos_prohibidos": ".env",
        "formatos_prohibidos": ".log,.tmp,.bak",
        "prompt": "",
        "patron": "",
        "solo_archivos_especificos": False,
    }

    def __init__(self):
        self.config = self._load_config()
        self._ensure_config_structure() # Asegurarse de que las claves principales existen

    def _ensure_config_structure(self):
        """Asegura que las claves principales existan en la configuración."""
        changed = False
        if "current_project" not in self.config:
            self.config["current_project"] = self.DEFAULT_CONFIG["current_project"]
            changed = True
        if "projects" not in self.config:
            self.config["projects"] = self.DEFAULT_CONFIG["projects"]
            changed = True
        if "project_metadata" not in self.config: # Añadir clave de metadatos si no existe
             self.config["project_metadata"] = self.DEFAULT_CONFIG["project_metadata"]
             changed = True
        if changed:
            self._save_config()


    def _load_config(self):
        """Carga la configuración desde el archivo JSON."""
        if not os.path.exists(self.CONFIG_FILE):
            return self.DEFAULT_CONFIG.copy() # Devuelve copia de los defaults si no existe
        try:
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error cargando {self.CONFIG_FILE}: {e}. Usando configuración por defecto.")
            return self.DEFAULT_CONFIG.copy()

    def _save_config(self):
        """Guarda la configuración actual en el archivo JSON."""
        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"Error guardando {self.CONFIG_FILE}: {e}")

    def get_projects(self):
        """Devuelve una lista de nombres de proyectos ordenados por fecha de último uso (más reciente primero)."""
        projects_data = []
        metadata = self.config.get("project_metadata", {})

        for name in self.config.get("projects", {}).keys():
            last_used = metadata.get(name, {}).get("last_used", 0) # Obtener timestamp, 0 si no existe
            projects_data.append({"name": name, "last_used": last_used})

        # Ordenar: Más reciente (mayor timestamp) primero. Los que tienen 0 van al final.
        projects_data.sort(key=lambda x: x["last_used"], reverse=True)

        return [p["name"] for p in projects_data] # Devolver solo los nombres ordenados

    def get_current_project(self):
        """Obtiene el nombre del proyecto actualmente seleccionado."""
        return self.config.get("current_project")

    def set_current_project(self, project_name):
        """Establece el proyecto actual y actualiza su timestamp de último uso."""
        if project_name in self.config.get("projects", {}):
            self.config["current_project"] = project_name

            # Actualizar timestamp de último uso
            if "project_metadata" not in self.config:
                 self.config["project_metadata"] = {}
            if project_name not in self.config["project_metadata"]:
                self.config["project_metadata"][project_name] = {}
            self.config["project_metadata"][project_name]["last_used"] = time.time() # Guardar timestamp actual

            self._save_config()
        elif project_name is None:
             self.config["current_project"] = None
             self._save_config()
        else:
             print(f"Advertencia: Intento de establecer proyecto actual a '{project_name}' que no existe.")


    def get_project_config(self, project_name):
        """Obtiene la configuración para un proyecto específico."""
        return self.config.get("projects", {}).get(project_name)

    def save_project_config(self, project_name, config_data):
        """Guarda la configuración para un proyecto específico."""
        if project_name in self.config.get("projects", {}):
            # Asegurarse de que todas las claves por defecto existen en config_data
            full_config_data = self.PROJECT_DEFAULTS.copy()
            full_config_data.update(config_data) # Actualiza con los valores proporcionados
            self.config["projects"][project_name] = full_config_data

            # Guardar la configuración general (que incluye este proyecto)
            # y actualizar el timestamp llamando a set_current_project
            self.set_current_project(project_name) # Esto guarda y actualiza el timestamp
            # self._save_config() # Ya no es necesario llamar a _save_config aquí directamente
        else:
             raise ValueError(f"El proyecto '{project_name}' no existe.")


    def create_new_project(self, project_name):
        """Crea una nueva configuración de proyecto con valores por defecto."""
        if not project_name or project_name.isspace():
             raise ValueError("El nombre del proyecto no puede estar vacío.")
        if project_name in self.config.get("projects", {}):
            raise ValueError(f"El proyecto '{project_name}' ya existe.")

        if "projects" not in self.config:
             self.config["projects"] = {}

        self.config["projects"][project_name] = self.PROJECT_DEFAULTS.copy()

        # No establecemos timestamp aquí, se hará cuando se seleccione o guarde por primera vez
        # via set_current_project.
        self._save_config() # Guardar la nueva estructura de proyectos

    # Podrías añadir funciones para eliminar o renombrar proyectos si es necesario