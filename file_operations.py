# file_operations.py
import os
import pyperclip

class FileProcessor:
    @staticmethod
    def _should_include(path, project_base_path, positive_patterns, negative_patterns):
        """
        Verifica si una ruta debe incluirse según patrones positivos y negativos.
        Los patrones se aplican case-insensitive a los componentes de la ruta
        relativa a project_base_path.
        """
        normalized_path_full = os.path.normpath(path).lower()
        normalized_project_base_path = os.path.normpath(project_base_path).lower()

        # Calcular la ruta relativa a la ruta base del proyecto
        if normalized_path_full.startswith(normalized_project_base_path):
            relative_path_str = os.path.relpath(normalized_path_full, normalized_project_base_path)
            # Si la ruta relativa es '.', significa que path es igual a project_base_path
            # En este caso, podríamos querer considerar el último componente de project_base_path
            # o simplemente tratarlo como una cadena vacía para que no coincida con patrones
            # destinados a nombres de archivo/directorio. Por ahora, si es '.', los componentes estarán vacíos.
            if relative_path_str == ".":
                # Considerar el nombre del directorio base si path es igual a project_base_path
                # path_components = [os.path.basename(normalized_project_base_path)] if normalized_project_base_path else []
                # O, para evitar que la propia ruta base coincida si no es la intención:
                path_components = []
            else:
                path_components = [comp for comp in relative_path_str.split(os.sep) if comp]
        else:
            # Si la ruta no está dentro de la ruta base del proyecto (caso raro aquí, pero defensivo)
            # Usamos los componentes de la ruta completa, pero esto podría no ser lo deseado.
            # O mejor, solo el nombre del archivo/directorio final
            path_components = [os.path.basename(normalized_path_full)]


        # 1. Comprobación de patrones negativos (case-insensitive)
        lower_negative_patterns = [p.lower() for p in negative_patterns]
        for neg_pattern in lower_negative_patterns:
            for component in path_components:
                if neg_pattern in component:
                    # print(f"DEBUG: Excluding '{path}' (relative: '{relative_path_str if normalized_path_full.startswith(normalized_project_base_path) else 'N/A'}') due to negative pattern '{neg_pattern}' in component '{component}'")
                    return False

        # 2. Comprobación de patrones positivos (si existen) (case-insensitive)
        if positive_patterns:
            found_positive_match = False
            lower_positive_patterns = [p.lower() for p in positive_patterns]
            for pos_pattern in lower_positive_patterns:
                for component in path_components:
                    if pos_pattern in component:
                        # print(f"DEBUG: Found positive match for '{path}' (relative: '{relative_path_str if normalized_path_full.startswith(normalized_project_base_path) else 'N/A'}') with pattern '{pos_pattern}' in component '{component}'")
                        found_positive_match = True
                        break
                if found_positive_match:
                    break

            if not found_positive_match:
                # print(f"DEBUG: Excluding '{path}' (relative: '{relative_path_str if normalized_path_full.startswith(normalized_project_base_path) else 'N/A'}') because no positive patterns matched components: {path_components}")
                return False

        # print(f"DEBUG: Including '{path}' (relative: '{relative_path_str if normalized_path_full.startswith(normalized_project_base_path) else 'N/A'}') components: {path_components}")
        return True

    @staticmethod
    def procesar_archivos(config, incluir_ruta):
        contenido_total = ""
        archivos_no_encontrados = []

        patrones_str = config.get("patrones", "").strip()
        all_patterns = [p.strip().lower() for p in patrones_str.split(',') if p.strip()]
        positive_patterns = [p[1:] for p in all_patterns if p.startswith('+') and len(p) > 1]
        negative_patterns = [p[1:] for p in all_patterns if p.startswith('-') and len(p) > 1]

        ruta_base = os.path.normpath(config["ruta_base"]) # Esta es la project_base_path para _should_include
        directorio_principal_str = config.get("directorio_principal", "").strip()
        nombres_directorios_principales = [d.strip() for d in directorio_principal_str.split(',') if d.strip()]

        rutas_de_busqueda = []
        if nombres_directorios_principales:
            for nombre_dir in nombres_directorios_principales:
                posible_ruta = os.path.join(ruta_base, nombre_dir)
                if os.path.isdir(posible_ruta):
                    rutas_de_busqueda.append(os.path.normpath(posible_ruta))
            if not rutas_de_busqueda:
                print(f"[Advertencia] Ninguno de los directorios principales especificados ({directorio_principal_str}) se encontró dentro de {ruta_base}. Buscando en toda la ruta base.")
                rutas_de_busqueda = [ruta_base]
        else:
            rutas_de_busqueda = [ruta_base]

        formatos_prohibidos = [
            f.strip().lower()
            for f in config.get("formatos_prohibidos", "").split(",")
            if f.strip()
        ]
        formatos_prohibidos = [
            f if f.startswith('.') else f'.{f}'
            for f in formatos_prohibidos
        ]

        directorios_prohibidos_config = [
            d.strip()
            for d in config.get("directorios_prohibidos", "").split(",")
            if d.strip()
        ]
        archivos_prohibidos_config = [
            a.strip()
            for a in config.get("archivos_prohibidos", "").split(",")
            if a.strip()
        ]

        solo_archivos_especificos = config.get("solo_archivos_especificos", False)
        processed_files = set()

        for directorio_busqueda in rutas_de_busqueda:
            if not solo_archivos_especificos:
                for root_dir, dirs, files in os.walk(directorio_busqueda, topdown=True):
                    # Filtrar directorios prohibidos por config y patrones negativos
                    dirs[:] = [
                        d for d in dirs
                        if d not in directorios_prohibidos_config and
                           FileProcessor._should_include(os.path.join(root_dir, d), ruta_base, [], negative_patterns)
                    ]

                    for archivo in files:
                        archivo_path = os.path.join(root_dir, archivo)
                        archivo_path_norm = os.path.normpath(archivo_path)

                        if archivo_path_norm in processed_files:
                            continue

                        if archivo in archivos_prohibidos_config:
                            continue
                        if os.path.splitext(archivo)[1].lower() in formatos_prohibidos:
                            continue

                        if FileProcessor._should_include(archivo_path, ruta_base, positive_patterns, negative_patterns):
                            contenido_total += FileProcessor._leer_archivo(
                                archivo_path,
                                ruta_base,
                                incluir_ruta
                            )
                            processed_files.add(archivo_path_norm)

        archivos_especificos = [
            a.strip()
            for a in config.get("archivos", "").split(",")
            if a.strip()
        ]
        for archivo_esp in archivos_especificos:
            archivo_objetivo_path = os.path.normpath(os.path.join(ruta_base, archivo_esp))
            archivo_encontrado = None

            if os.path.isfile(archivo_objetivo_path):
                archivo_encontrado = archivo_objetivo_path
            else:
                nombre_archivo_objetivo = os.path.basename(archivo_esp)
                for directorio_busqueda_esp in rutas_de_busqueda: # Buscar en todas las rutas de búsqueda definidas
                    archivo_path_temporal = FileProcessor._buscar_archivo_recursivo(
                        directorio_busqueda_esp,
                        nombre_archivo_objetivo,
                        directorios_prohibidos_config # Pasar dirs prohibidos para la búsqueda
                    )
                    if archivo_path_temporal:
                        archivo_encontrado = archivo_path_temporal
                        break

            if archivo_encontrado:
                archivo_encontrado_norm = os.path.normpath(archivo_encontrado)
                if archivo_encontrado_norm in processed_files:
                    continue

                if os.path.splitext(archivo_encontrado)[1].lower() in formatos_prohibidos:
                    continue

                # Usar ruta_base del proyecto para la evaluación de _should_include
                if FileProcessor._should_include(archivo_encontrado, ruta_base, positive_patterns, negative_patterns):
                    contenido_total += FileProcessor._leer_archivo(
                        archivo_encontrado,
                        ruta_base,
                        incluir_ruta
                    )
                    processed_files.add(archivo_encontrado_norm)
                else:
                    if archivo_esp not in [a.split(' ')[0] for a in archivos_no_encontrados]:
                        archivos_no_encontrados.append(f"{archivo_esp} (filtrado por patrones)")
            else:
                if archivo_esp not in [a.split(' ')[0] for a in archivos_no_encontrados]:
                     archivos_no_encontrados.append(f"{archivo_esp} (no hallado)")

        return contenido_total, archivos_no_encontrados

    @staticmethod
    def _buscar_archivo_recursivo(ruta_a_buscar, nombre_objetivo, directorios_prohibidos_config):
        nombre_objetivo_lower = nombre_objetivo.lower()
        for root, dirs, files in os.walk(ruta_a_buscar, topdown=True):
            dirs[:] = [d for d in dirs if d not in directorios_prohibidos_config]
            for file in files:
                if file.lower() == nombre_objetivo_lower:
                    return os.path.join(root, file)
        return None

    @staticmethod
    def _leer_archivo(archivo_path, ruta_base_proyecto, incluir_ruta): # ruta_base_proyecto para os.relpath
        try:
            with open(archivo_path, "r", encoding="utf-8", errors='ignore') as f:
                contenido = f.read()
                if incluir_ruta:
                    try:
                        norm_archivo_path = os.path.normpath(archivo_path)
                        norm_ruta_base_proyecto = os.path.normpath(ruta_base_proyecto)

                        # Asegurarse que la ruta del archivo esté dentro de la ruta base del proyecto
                        # antes de calcular la ruta relativa.
                        if os.path.commonpath([norm_archivo_path, norm_ruta_base_proyecto]) == norm_ruta_base_proyecto:
                            relative_path = os.path.relpath(norm_archivo_path, start=norm_ruta_base_proyecto).replace("\\", "/")
                        else:
                            # Si el archivo está fuera de la ruta_base_proyecto (ej. un archivo específico con ruta absoluta)
                            # mostrar solo el nombre del archivo o la ruta absoluta como fallback.
                            relative_path = os.path.basename(norm_archivo_path) + " (fuera de ruta base)"
                            # Opcionalmente, podrías querer mostrar la ruta absoluta si es muy diferente:
                            # relative_path = norm_archivo_path.replace("\\", "/") + " (ruta absoluta)"

                    except ValueError:
                        relative_path = os.path.basename(archivo_path) + " (error al calcular ruta relativa)"
                    return f"\n--- START FILE: {relative_path} ---\n{contenido}\n--- END FILE: {relative_path} ---\n"
                else:
                    nombre_archivo = os.path.basename(archivo_path)
                    return f"\n--- START FILE: {nombre_archivo} ---\n{contenido}\n--- END FILE: {nombre_archivo} ---\n"
        except Exception as e:
            print(f"Error leyendo archivo {archivo_path}: {str(e)}")
            try:
                relative_path_err = os.path.relpath(archivo_path, start=ruta_base_proyecto).replace("\\", "/")
            except ValueError:
                relative_path_err = os.path.basename(archivo_path) + " (ruta no relativa)"
            except Exception:
                relative_path_err = archivo_path
            return f"\n--- ERROR READING FILE: {relative_path_err} ({str(e)}) ---\n"