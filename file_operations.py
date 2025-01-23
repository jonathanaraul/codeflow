# file_operations.py
import os
import pyperclip

class FileProcessor:
    @staticmethod
    def procesar_archivos(config, incluir_ruta):
        contenido_total = ""
        archivos_no_encontrados = []
        
        directorio_completo = os.path.normpath(
            os.path.join(config["ruta_base"], config["directorio_principal"])
        ) if config["directorio_principal"] else os.path.normpath(config["ruta_base"])

        # Procesar formatos prohibidos
        formatos_prohibidos = [f.strip().lower() for f in config.get("formatos_prohibidos", "").split(",") if f.strip()]
        formatos_prohibidos = [f if f.startswith('.') else f'.{f}' for f in formatos_prohibidos]  # Normalizar extensiones

        # Procesamiento de directorios
        if os.path.isdir(directorio_completo):
            directorios_prohibidos = [d.strip() for d in config["directorios_prohibidos"].split(",") if d.strip()]
            archivos_prohibidos = [a.strip() for a in config["archivos_prohibidos"].split(",") if a.strip()]
            
            for root_dir, dirs, files in os.walk(directorio_completo):
                dirs[:] = [d for d in dirs if d not in directorios_prohibidos]
                
                # Filtrar por nombre y formato
                files = [f for f in files 
                        if f not in archivos_prohibidos 
                        and os.path.splitext(f)[1].lower() not in formatos_prohibidos]
                
                for archivo in files:
                    archivo_path = os.path.join(root_dir, archivo)
                    contenido_total += FileProcessor._leer_archivo(archivo_path, config["ruta_base"], incluir_ruta)

        # Procesamiento de archivos específicos
        archivos_especificos = [a.strip() for a in config["archivos"].split(",") if a.strip()]
        for archivo in archivos_especificos:
            archivo_path = os.path.normpath(os.path.join(config["ruta_base"], archivo))
            
            # Verificar si el formato está prohibido
            extension = os.path.splitext(archivo_path)[1].lower()
            if extension in formatos_prohibidos:
                continue
            
            if os.path.isfile(archivo_path):
                contenido_total += FileProcessor._leer_archivo(archivo_path, config["ruta_base"], incluir_ruta)
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