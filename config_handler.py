# config_handler.py
import os
import json
import jsonschema

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "projects": {
            "type": "object",
            "patternProperties": {
                "^.*$": {
                    "type": "object",
                    "properties": {
                        "ruta_base": {"type": "string"},
                        "directorio_principal": {"type": "string"},
                        "archivos": {"type": "string"},
                        "directorios_prohibidos": {"type": "string"},
                        "archivos_prohibidos": {"type": "string"},
                        "formatos_prohibidos": {"type": "string"},  # Nuevo campo
                        "prompt": {"type": "string"}
                    },
                    "required": ["ruta_base", "directorio_principal", "archivos", 
                               "directorios_prohibidos", "archivos_prohibidos"]
                }
            }
        },
        "current_project": {"type": "string"}
    },
    "required": ["projects", "current_project"]
}

class ConfigHandler:
    def __init__(self, config_file="projects_config.json"):
        self.config_file = config_file
        self._initialize_config_file()

    def _initialize_config_file(self):
        if not os.path.exists(self.config_file):
            base_config = {
                "projects": {},
                "current_project": ""
            }
            self._save_config(base_config)

    def _load_config(self):
        with open(self.config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        jsonschema.validate(instance=config, schema=CONFIG_SCHEMA)
        return config

    def _save_config(self, config):
        jsonschema.validate(instance=config, schema=CONFIG_SCHEMA)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

    def get_projects(self):
        return list(self._load_config()["projects"].keys())

    def get_current_project(self):
        config = self._load_config()
        return config["current_project"]

    def set_current_project(self, project_name):
        config = self._load_config()
        if project_name not in config["projects"]:
            raise ValueError(f"Proyecto {project_name} no existe")
        config["current_project"] = project_name
        self._save_config(config)

    def get_project_config(self, project_name):
        config = self._load_config()
        return config["projects"].get(project_name, None)

    def save_project_config(self, project_name, config_data):
        config = self._load_config()
        config["projects"][project_name] = config_data
        self._save_config(config)

    def create_new_project(self, project_name):
        config = self._load_config()
        if project_name in config["projects"]:
            raise ValueError(f"El proyecto {project_name} ya existe")
        
        config["projects"][project_name] = {
            "ruta_base": "",
            "directorio_principal": "",
            "archivos": "",
            "directorios_prohibidos": "",
            "archivos_prohibidos": "",
            "formatos_prohibidos": "",  # Nuevo campo inicializado
            "prompt": ""
        }
        self._save_config(config)