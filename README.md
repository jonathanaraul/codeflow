# CodeFlow 🚀

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

Gestor de proyectos para programadores que facilita la organización y preparación de contexto para LLMs.

**Autor:** Jonathan Araul  
**Ubicación:** Maturín, Venezuela  
**Contacto:** [jonathan.araul@gmail.com](mailto:jonathan.araul@gmail.com)

## Características Principales ✨

- 🗂️ Gestión de múltiples proyectos
- 📋 Configuración personalizable de:
  - Rutas base
  - Directorios/archivos prohibidos
  - Formatos excluidos
- 📝 Sistema de prompts y solicitudes
- 📋 Copiado automático al portapapeles
- 🎨 Interfaz de usuario moderna con tema oscuro

## Instalación 🔧

```bash
# Clonar repositorio
git clone https://github.com/jonathanaraul/codeflow.git

# Entrar al directorio
cd codeflow

# Instalar dependencias (recomendado usar entorno virtual)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Uso 🖥️

1. **Iniciar aplicación:**
   
   ```bash
   python main.py
   ```

2. **Crear nuevo proyecto:**  
   Click en "➕ Nuevo Proyecto"

3. **Configurar rutas y exclusiones:**  
   
   - Seleccionar ruta base  
   - Definir directorios/archivos prohibidos

4. **Trabajar con prompts:**  
   
   - Escribir contexto permanente en "Prompt de Contexto"  
   - Agregar solicitudes temporales

5. **Copiar y guardar:**  
   Usar botón "⎘ Copiar y Guardar"

## Configuración ⚙️

Los proyectos se guardan en `projects_config.json` con:

```json
{
    "projects": {
        "nombre_proyecto": {
            "ruta_base": "...",
            "directorio_principal": "...",
            "archivos": "...",
            "directorios_prohibidos": "...",
            "archivos_prohibidos": "...",
            "formatos_prohibidos": "...",
            "prompt": "..."
        }
    }
}
```

## Capturas de Pantalla 🖼️

![Interfaz Principal](https://ejemplo.com/captura-codeflow.jpg)

## Licencia 📄

Licencia GPL (General Public License) - Ver [LICENSE](LICENSE) para más detalles.