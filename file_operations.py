# file_operations.py
import os
import pyperclip

class FileProcessor:
    @staticmethod
    def procesar_archivos(config, incluir_ruta):
        contenido_total = ""
        archivos_no_encontrados = []

        # --- Cambio: Procesar múltiples patrones separados por coma ---
        patron_str = config.get("patron", "").strip()
        patrones = [p.strip().lower() for p in patron_str.split(',') if p.strip()]

        # --- Cambio: Procesar múltiples directorios principales y buscar dentro de ruta_base ---
        ruta_base = os.path.normpath(config["ruta_base"])
        directorios_principales_str = config.get("directorio_principal", "").strip()
        nombres_directorios_principales = [d.strip() for d in directorios_principales_str.split(',') if d.strip()]

        rutas_de_busqueda = []
        if nombres_directorios_principales:
            for nombre_dir in nombres_directorios_principales:
                # Buscar el directorio *dentro* de la ruta base
                posible_ruta = os.path.join(ruta_base, nombre_dir)
                if os.path.isdir(posible_ruta):
                    rutas_de_busqueda.append(os.path.normpath(posible_ruta))
            if not rutas_de_busqueda:
                print(f"[Advertencia] Ninguno de los directorios principales especificados ({directorios_principales_str}) se encontró dentro de {ruta_base}. Buscando en toda la ruta base.")
                # Si no se encontró ninguno, usar la ruta base como única ruta de búsqueda
                rutas_de_busqueda = [ruta_base]
        else:
            # Si no se especificaron directorios principales, usar la ruta base
            rutas_de_busqueda = [ruta_base]
        # --- Fin Cambio ---

        # Procesar formatos prohibidos
        formatos_prohibidos = [
            f.strip().lower()
            for f in config.get("formatos_prohibidos", "").split(",")
            if f.strip()
        ]
        formatos_prohibidos = [
            f if f.startswith('.') else f'.{f}'
            for f in formatos_prohibidos
        ]  # Normalizar extensiones

        solo_archivos_especificos = config.get("solo_archivos_especificos", False)

        # --- Cambio: Iterar sobre las rutas de búsqueda determinadas ---
        for directorio_busqueda in rutas_de_busqueda:
            # Procesamiento de directorios (solo si no se marca "Solo archivos específicos")
            if not solo_archivos_especificos: # and os.path.isdir(directorio_busqueda): # ya validamos isdir antes
                directorios_prohibidos = [
                    d.strip()
                    for d in config.get("directorios_prohibidos", "").split(",")
                    if d.strip()
                ]
                archivos_prohibidos = [
                    a.strip()
                    for a in config.get("archivos_prohibidos", "").split(",")
                    if a.strip()
                ]

                for root_dir, dirs, files in os.walk(directorio_busqueda):
                    # Excluir directorios prohibidos
                    dirs[:] = [d for d in dirs if d not in directorios_prohibidos]

                    # Filtrar archivos prohibidos, formatos prohibidos y aplicar patrón si está definido
                    files_filtrados = []
                    for archivo in files:
                        if archivo in archivos_prohibidos:
                            continue
                        if os.path.splitext(archivo)[1].lower() in formatos_prohibidos:
                            continue

                        # --- Lógica OR para múltiples patrones ---
                        if patrones and not any(p in archivo.lower() for p in patrones):
                            continue # Saltar archivo si no coincide con ningún patrón

                        files_filtrados.append(archivo)

                    for archivo in files_filtrados:
                        archivo_path = os.path.join(root_dir, archivo)
                        contenido_total += FileProcessor._leer_archivo(
                            archivo_path,
                            ruta_base, # Relativo siempre a la ruta base original del proyecto
                            incluir_ruta
                        )
        # --- Fin Cambio ---

        # Procesamiento de archivos específicos
        archivos_especificos = [
            a.strip()
            for a in config.get("archivos", "").split(",")
            if a.strip()
        ]
        for archivo in archivos_especificos:
            nombre_archivo = os.path.basename(archivo)

            # --- Aplicar lógica OR para múltiples patrones a archivos específicos ---
            if patrones and not any(p in nombre_archivo.lower() for p in patrones):
                continue # Saltar si el nombre del archivo no coincide con ningún patrón

            # --- Cambio: Buscar el archivo en TODAS las rutas de búsqueda válidas ---
            archivo_encontrado = None
            for directorio_busqueda in rutas_de_busqueda:
                archivo_path_temporal = FileProcessor._buscar_archivo(
                    directorio_busqueda,
                    nombre_archivo,
                    [d.strip() for d in config.get("directorios_prohibidos", "").split(",") if d.strip()]
                )
                if archivo_path_temporal:
                    archivo_encontrado = archivo_path_temporal
                    break # Encontrar la primera ocurrencia y usarla

            if archivo_encontrado:
                 # Verificar que el formato no esté prohibido
                if os.path.splitext(archivo_encontrado)[1].lower() in formatos_prohibidos:
                    continue
                contenido_total += FileProcessor._leer_archivo(
                    archivo_encontrado,
                    ruta_base, # Relativo siempre a la ruta base original del proyecto
                    incluir_ruta
                )
            else:
                archivos_no_encontrados.append(archivo)
            # --- Fin Cambio ---

        return contenido_total, archivos_no_encontrados

    @staticmethod
    def _buscar_archivo(ruta_a_buscar, nombre_objetivo, directorios_prohibidos):
        """
        Recorre recursivamente la ruta_a_buscar buscando un archivo cuyo nombre (case-insensitive)
        coincida exactamente con nombre_objetivo. Se omiten los directorios que están en la lista
        de directorios_prohibidos.
        """
        for root, dirs, files in os.walk(ruta_a_buscar):
            # Excluir directorios prohibidos
            dirs[:] = [d for d in dirs if d not in directorios_prohibidos]
            for file in files:
                if file.lower() == nombre_objetivo.lower():
                    return os.path.join(root, file)
        return None

    @staticmethod
    def _leer_archivo(archivo_path, ruta_base, incluir_ruta):
        try:
            # Usar 'ignore' para evitar errores con caracteres inválidos
            with open(archivo_path, "r", encoding="utf-8", errors='ignore') as f:
                contenido = f.read()
                if incluir_ruta:
                    # Normalizar la ruta relativa para usar separadores '/' consistentemente
                    relative_path = os.path.relpath(archivo_path, start=ruta_base).replace("\\", "/")
                    # Añadir delimitadores claros
                    return f"\n--- START FILE: {relative_path} ---\n{contenido}\n--- END FILE: {relative_path} ---\n"
                else:
                     # Añadir delimitadores incluso sin ruta
                     nombre_archivo = os.path.basename(archivo_path)
                     return f"\n--- START FILE: {nombre_archivo} ---\n{contenido}\n--- END FILE: {nombre_archivo} ---\n"
        except Exception as e:
            print(f"Error leyendo archivo {archivo_path}: {str(e)}")
            # Devolver un marcador de error en lugar de string vacío
            relative_path_err = os.path.relpath(archivo_path, start=ruta_base).replace("\\", "/")
            return f"\n--- ERROR READING FILE: {relative_path_err} ({str(e)}) ---\n"