# file_operations.py
import os
import pyperclip

class FileProcessor:
    @staticmethod
    def _should_include(path, positive_patterns, negative_patterns):
        """
        Verifica si una ruta debe incluirse según patrones positivos y negativos.
        Los patrones se aplican case-insensitive a cada componente de la ruta.
        """
        normalized_path = os.path.normpath(path).lower()
        # Split path into components, handling potential empty strings from separators
        path_components = [comp for comp in normalized_path.split(os.sep) if comp]

        # 1. Comprobación de patrones negativos (case-insensitive)
        # Convert patterns to lowercase once outside the loop for efficiency
        lower_negative_patterns = [p.lower() for p in negative_patterns]
        for neg_pattern in lower_negative_patterns:
            for component in path_components:
                if neg_pattern in component:
                    # print(f"DEBUG: Excluding '{path}' due to negative pattern '{neg_pattern}' in component '{component}'") # Debugging
                    return False # Excluir si cualquier parte coincide con un patrón negativo

        # 2. Comprobación de patrones positivos (si existen) (case-insensitive)
        if positive_patterns:
            found_positive_match = False
            # Convert patterns to lowercase once outside the loop for efficiency
            lower_positive_patterns = [p.lower() for p in positive_patterns]
            for pos_pattern in lower_positive_patterns:
                for component in path_components:
                    if pos_pattern in component:
                        # print(f"DEBUG: Found positive match for '{path}' with pattern '{pos_pattern}' in component '{component}'") # Debugging
                        found_positive_match = True
                        break # Encontró coincidencia para este patrón positivo, no necesita seguir con los componentes
                if found_positive_match:
                    break # Encontró al menos una coincidencia positiva general, no necesita seguir con los patrones

            if not found_positive_match:
                # print(f"DEBUG: Excluding '{path}' because no positive patterns matched.") # Debugging
                return False # Excluir si se especificaron patrones positivos y ninguno coincidió

        # Si pasó todas las comprobaciones (o no había positivas), incluir
        # print(f"DEBUG: Including '{path}'") # Debugging
        return True

    @staticmethod
    def procesar_archivos(config, incluir_ruta):
        contenido_total = ""
        archivos_no_encontrados = []

        # --- Cambio: Procesar múltiples patrones positivos/negativos ---
        patrones_str = config.get("patrones", "").strip() # Usar nueva clave "patrones"
        all_patterns = [p.strip().lower() for p in patrones_str.split(',') if p.strip()]
        # *** CORRECCIÓN AQUÍ: Extraer correctamente patrones + y - ***
        positive_patterns = [p[1:] for p in all_patterns if p.startswith('+') and len(p) > 1] # <<< CORREGIDO: Buscar '+' y quitarlo
        negative_patterns = [p[1:] for p in all_patterns if p.startswith('-') and len(p) > 1] # Quitar '-' y asegurarse de que no sea solo '-'
        # print(f"DEBUG: Positive Patterns: {positive_patterns}") # Debugging
        # print(f"DEBUG: Negative Patterns: {negative_patterns}") # Debugging
        # --- Fin Cambio ---

        ruta_base = os.path.normpath(config["ruta_base"])
        directorios_principales_str = config.get("directorio_principal", "").strip()
        nombres_directorios_principales = [d.strip() for d in directorios_principales_str.split(',') if d.strip()]

        rutas_de_busqueda = []
        if nombres_directorios_principales:
            for nombre_dir in nombres_directorios_principales:
                posible_ruta = os.path.join(ruta_base, nombre_dir)
                if os.path.isdir(posible_ruta):
                    rutas_de_busqueda.append(os.path.normpath(posible_ruta))
            if not rutas_de_busqueda:
                print(f"[Advertencia] Ninguno de los directorios principales especificados ({directorios_principales_str}) se encontró dentro de {ruta_base}. Buscando en toda la ruta base.")
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

        # Keep track of processed files to avoid duplicates if specific files are also found during walk
        processed_files = set()

        for directorio_busqueda in rutas_de_busqueda:
            if not solo_archivos_especificos:
                for root_dir, dirs, files in os.walk(directorio_busqueda, topdown=True):
                    # Filtrar directorios prohibidos por config ANTES de descender
                    # También aplicar patrones negativos a directorios aquí
                    # Nota: Si hay patrones positivos, *no* filtramos directorios aquí basados en ellos,
                    # porque un archivo dentro de un directorio no coincidente *podría* coincidir.
                    # La decisión final se toma a nivel de archivo/directorio específico con _should_include.
                    dirs[:] = [
                        d for d in dirs
                        if d not in directorios_prohibidos_config and
                           FileProcessor._should_include(os.path.join(root_dir, d), [], negative_patterns) # Solo check negativo aquí
                           # El check positivo se hará después en la ruta completa
                    ]


                    for archivo in files:
                        archivo_path = os.path.join(root_dir, archivo)
                        archivo_path_norm = os.path.normpath(archivo_path) # Normalize for set

                        if archivo_path_norm in processed_files:
                            continue # Skip if already processed as a specific file

                        # Comprobaciones básicas de exclusión primero
                        if archivo in archivos_prohibidos_config:
                            continue
                        if os.path.splitext(archivo)[1].lower() in formatos_prohibidos:
                            continue

                        # Aplicar patrones positivos/negativos al archivo/ruta COMPLETA
                        if FileProcessor._should_include(archivo_path, positive_patterns, negative_patterns):
                            contenido_total += FileProcessor._leer_archivo(
                                archivo_path,
                                ruta_base, # Relativo siempre a la ruta base original del proyecto
                                incluir_ruta
                            )
                            processed_files.add(archivo_path_norm) # Mark as processed


        # Procesamiento de archivos específicos
        archivos_especificos = [
            a.strip()
            for a in config.get("archivos", "").split(",")
            if a.strip()
        ]
        for archivo_esp in archivos_especificos:
            # Intenta usar la ruta relativa dada en config si es posible, sino busca por nombre base
            archivo_objetivo_path = os.path.normpath(os.path.join(ruta_base, archivo_esp))

            if os.path.isfile(archivo_objetivo_path):
                 archivo_encontrado = archivo_objetivo_path
            else:
                # Si no se encontró como ruta relativa/absoluta, busca por nombre de archivo recursivamente
                nombre_archivo_objetivo = os.path.basename(archivo_esp)
                archivo_encontrado = None
                for directorio_busqueda in rutas_de_busqueda:
                    archivo_path_temporal = FileProcessor._buscar_archivo_recursivo(
                        directorio_busqueda,
                        nombre_archivo_objetivo,
                        directorios_prohibidos_config
                    )
                    if archivo_path_temporal:
                        archivo_encontrado = archivo_path_temporal
                        break

            if archivo_encontrado:
                archivo_encontrado_norm = os.path.normpath(archivo_encontrado)
                if archivo_encontrado_norm in processed_files:
                    continue # Skip if already processed during walk

                # Verificar formato prohibido
                if os.path.splitext(archivo_encontrado)[1].lower() in formatos_prohibidos:
                    continue

                # Aplicar patrones positivos/negativos al archivo específico encontrado
                if FileProcessor._should_include(archivo_encontrado, positive_patterns, negative_patterns):
                    contenido_total += FileProcessor._leer_archivo(
                        archivo_encontrado,
                        ruta_base, # Relativo siempre a la ruta base original del proyecto
                        incluir_ruta
                    )
                    processed_files.add(archivo_encontrado_norm) # Mark as processed
                else:
                    # Si no pasó el filtro _should_include pero se especificó, añadir a no encontrados
                    # Esto cubre el caso donde un archivo específico no coincide con patrones + o coincide con -
                    if archivo_esp not in [a.split(' ')[0] for a in archivos_no_encontrados]: # Evitar duplicados en el mensaje
                       archivos_no_encontrados.append(f"{archivo_esp} (filtrado por patrones)")

            else:
                 # Solo añadir a no encontrados si la búsqueda recursiva falló
                 if archivo_esp not in [a.split(' ')[0] for a in archivos_no_encontrados]: # Evitar duplicados en el mensaje
                    archivos_no_encontrados.append(f"{archivo_esp} (no hallado)")


        return contenido_total, archivos_no_encontrados

    @staticmethod
    def _buscar_archivo_recursivo(ruta_a_buscar, nombre_objetivo, directorios_prohibidos_config):
        """
        Busca recursivamente un archivo por nombre exacto (case-insensitive)
        dentro de una ruta, respetando los directorios prohibidos de la configuración.
        Devuelve la ruta completa del primer archivo encontrado o None.
        """
        nombre_objetivo_lower = nombre_objetivo.lower()
        for root, dirs, files in os.walk(ruta_a_buscar, topdown=True):
            # Filtrar directorios prohibidos antes de descender
            dirs[:] = [d for d in dirs if d not in directorios_prohibidos_config]

            for file in files:
                if file.lower() == nombre_objetivo_lower:
                    return os.path.join(root, file)
        return None # No encontrado en esta ruta_a_buscar


    @staticmethod
    def _leer_archivo(archivo_path, ruta_base, incluir_ruta):
        try:
            with open(archivo_path, "r", encoding="utf-8", errors='ignore') as f:
                contenido = f.read()
                if incluir_ruta:
                    # Ensure relative path calculation is robust
                    try:
                        # Normalizar ambas rutas antes de calcular la relativa
                        norm_archivo_path = os.path.normpath(archivo_path)
                        norm_ruta_base = os.path.normpath(ruta_base)
                        if os.path.commonpath([norm_archivo_path, norm_ruta_base]) == norm_ruta_base:
                           relative_path = os.path.relpath(norm_archivo_path, start=norm_ruta_base).replace("\\", "/")
                        else: # Si no está bajo ruta_base, usar nombre de archivo
                            relative_path = os.path.basename(norm_archivo_path) + " (ruta no relativa)"
                    except ValueError: # Fallback por si acaso
                         relative_path = os.path.basename(archivo_path) + " (error al calcular ruta relativa)"
                    return f"\n--- START FILE: {relative_path} ---\n{contenido}\n--- END FILE: {relative_path} ---\n"
                else:
                    nombre_archivo = os.path.basename(archivo_path)
                    return f"\n--- START FILE: {nombre_archivo} ---\n{contenido}\n--- END FILE: {nombre_archivo} ---\n"
        except Exception as e:
            print(f"Error leyendo archivo {archivo_path}: {str(e)}")
            # Intentar obtener la ruta relativa para el mensaje de error también
            try:
                 relative_path_err = os.path.relpath(archivo_path, start=ruta_base).replace("\\", "/")
            except ValueError:
                 relative_path_err = os.path.basename(archivo_path) + " (ruta no relativa)"
            except Exception: # Otro fallback
                 relative_path_err = archivo_path

            return f"\n--- ERROR READING FILE: {relative_path_err} ({str(e)}) ---\n"