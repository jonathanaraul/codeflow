# file_operations.py
import os
import pyperclip

class FileProcessor:
    @staticmethod
    def procesar_archivos(config, incluir_ruta):
        contenido_total = ""
        archivos_no_encontrados = []
        
        # Procesar formatos prohibidos
        formatos_prohibidos = [
            f if f.startswith('.') else f'.{f}'
            for f in (
                ff.strip().lower()
                for ff in config.get("formatos_prohibidos", "").split(",")
                if ff.strip()
            )
        ]
        
        # Si NO está marcado "buscar_solo_especificos", se realiza el escaneo de directorios
        if not config.get("buscar_solo_especificos", False):
            # Manejo de múltiples directorios
            directorios_list = [
                d.strip() for d in config.get("directorios", "").split(",") if d.strip()
            ]
            
            # Si no hay directorios listados, usar el campo antiguo como fallback
            if not directorios_list:
                directorios_list = [config["directorio_principal"]]
            
            directorios_prohibidos = [
                dp.strip() for dp in config["directorios_prohibidos"].split(",") if dp.strip()
            ]
            archivos_prohibidos = [
                ap.strip() for ap in config["archivos_prohibidos"].split(",") if ap.strip()
            ]
            
            for directorio in directorios_list:
                # Construir ruta completa
                full_dir = (os.path.normpath(os.path.join(config["ruta_base"], directorio))
                            if directorio
                            else os.path.normpath(config["ruta_base"]))
                
                # Verificar que sea un directorio válido
                if os.path.isdir(full_dir):
                    for root_dir, dirs, files in os.walk(full_dir):
                        # Filtrar directorios prohibidos
                        dirs[:] = [d for d in dirs if d not in directorios_prohibidos]
                        
                        # Filtrar archivos prohibidos y formatos prohibidos
                        files = [
                            f for f in files
                            if f not in archivos_prohibidos
                            and os.path.splitext(f)[1].lower() not in formatos_prohibidos
                        ]
                        
                        for archivo in files:
                            archivo_path = os.path.join(root_dir, archivo)
                            contenido_total += FileProcessor._leer_archivo(
                                archivo_path,
                                config["ruta_base"],
                                incluir_ruta
                            )
        
        # Procesamiento de archivos específicos (siempre se hace)
        archivos_especificos = [a.strip() for a in config["archivos"].split(",") if a.strip()]
        for archivo in archivos_especificos:
            archivo_path = os.path.normpath(os.path.join(config["ruta_base"], archivo))
            
            # Verificar si el formato está prohibido
            extension = os.path.splitext(archivo_path)[1].lower()
            if extension in formatos_prohibidos:
                continue
            
            if os.path.isfile(archivo_path):
                contenido_total += FileProcessor._leer_archivo(
                    archivo_path,
                    config["ruta_base"],
                    incluir_ruta
                )
            else:
                archivos_no_encontrados.append(archivo)

        return contenido_total, archivos_no_encontrados

    @staticmethod
    def _leer_archivo(archivo_path, ruta_base, incluir_ruta):
        try:
            with open(archivo_path, "r", encoding="utf-8") as f:
                contenido = f.read()
                if incluir_ruta:
                    relative_path = os.path.relpath(archivo_path, start=ruta_base)
                    return f"\n{relative_path}\n{contenido}"
                return contenido
        except Exception as e:
            print(f"Error leyendo archivo {archivo_path}: {str(e)}")
            return ""
