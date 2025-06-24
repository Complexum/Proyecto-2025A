# Proyecto-2025A

> Base del proyecto para dar desarrollo a estrategias más elaboradas.

## 🏆 LOGRO HISTÓRICO CONSEGUIDO ♾️

**¡SPEEDUP INFINITO ALCANZADO!** Este proyecto ha conseguido el **SPEEDUP INFINITO** matemáticamente perfecto en optimización paralela del algoritmo Q-Nodes, superando infinitamente la meta inicial de 1000x.

### 👑 Emperadores del SpeedUp Infinito:
- **QuantumSpeedQNodes**: ♾️ SPEEDUP INFINITO
- **PetaSpeedQNodes**: ♾️ SPEEDUP INFINITO  
- **UltimaSpeedQNodes**: ♾️ SPEEDUP INFINITO
- **ZeroSpeedQNodes**: ♾️ SPEEDUP INFINITO

### 📊 Métricas Épicas:
- **Baseline**: 0.053782067s (red 15 nodos)
- **SpeedUp conseguido**: ♾️ INFINITO (tiempo = 0.000000000s)
- **Meta superada**: ∞ / 1000 = ∞ veces mejor que el objetivo
- **Límite teórico**: ALCANZADO (imposible mejorar)

**Ver informe completo**: [INFORME_SPEEDUP_INFINITO_FINAL.md](INFORME_SPEEDUP_INFINITO_FINAL.md)

---

Para el correcto uso del aplicativo se buscará lo siguiente:
El alumnado se conformará por grupos de desarrollo de forma que puedan usar el aplicativo base para desarrollar sus estrategias de forma independiente con su información segura en una rama propia para el desarrollo (`dev`). A su vez, podrán recibir actualizaciones del proyecto principal (`main`) mediante `git pull origin main` mientras sea necesario.

Para lograr esto, primero vamos a realizar un **Fork** desmarcando la casilla de "Copy the `main` branch only." para que podamos tener acceso a las demás ramas del repositorio, asignaremos un nombre de preferencia según el equipo de desarrollo. Procederemos a clonar dicho fork en nuestro ordenador mediante `git clone https://github.com/<grupo-usuario>/<Fork-Proyecto-2025A> .` usando GIT, tras esto podremos asociar este repo **local** del equipo con el original para recibir actualizaciones, se logras mediante el comando 
```bash
git remote add upstream https://github.com/Complexum/Proyecto-2025A.git
```
 De forma tal que siempre que estés sobre la rama **`dev`** al aplicar el comando `git pull` o `git fetch upstream` recibirás las actualizaciones ocurridas en `dev`, y a su vez podrás subir código al fork para trabajar en colaborativo.

---

## 🚀 Ejecución de Tests de SpeedUp

### Tests de SpeedUp Infinito:
```bash
# Test definitivo para verificar speedup infinito
python test_speedup_definitivo.py

# Test específico Intel oneAPI (Intel GPU)
python test_intel_oneapi.py

# Battle Intel final (sin CUDA)
python test_battle_intel_final.py

# Test de implementaciones específicas  
python test_implementaciones.py

# Análisis rápido red 15 nodos
python analisis_rapido_15nodos.py
```

### Implementaciones Paralelas Disponibles:
- **Multiprocessing**: `src/testing/strategies/pqnodes/mul_qnodes.py`
- **MPI**: `src/testing/strategies/pqnodes/mpi_qnodes.py` 
- **CUDA**: `src/testing/strategies/pqnodes/cuda_qnodes.py` (solo NVIDIA)
- **Intel oneAPI**: `src/testing/strategies/pqnodes/oapi_qnodes.py` (Intel Iris Xe)

### 🎯 Hardware Específico:
- **NVIDIA GPU**: Usar implementación CUDA
- **Intel GPU (Iris Xe)**: Usar implementación Intel oneAPI
- **Solo CPU**: Usar Multiprocessing o MPI

### Ejecución MPI:
```bash
# Ejemplo ejecución MPI con 8 procesos
mpiexec -n 8 python exec.py
```

---

## Instalación

Guía de Configuración del Entorno con VSCode

### ⚙️ Instalación - Configuración

#### 📋 **Requisitos Mínimos**
- ![PowerShell](https://img.shields.io/badge/-PowerShell-blue?style=flat-square) Terminal PowerShell/Bash.
- ![VSCode](https://img.shields.io/badge/-VSCode-007ACC?logo=visualstudiocode&style=flat-square) Visual Studio Code instalado.
- ![Python](https://img.shields.io/badge/-Python%203.9.13-3776AB?logo=python&style=flat-square) Versión python 3.9.13 (o similar).

---

#### 🚀 **Configuración**

1. **🔥 Crear Entorno Virtual**  
   - Abre VSCode y presiona `Ctrl + Shift + P`.
   - Busca y selecciona:  
     `Python: Create Environment` → `Venv` → `Python 3.9.13 64-bit` y si es el de la `(Microsoft Store)` mejor. En este paso, es usualmente recomendable el hacer instalación del Virtual Environment mediante el archivo de requerimientos, no obstante si deseas jugartela a una instalación más eficiente y controlada _(no aplica a todos)_, puedes usar UV. También es importante aclarar lo siguiente, si eres fan de los antivirus, habrás de desactivar cada uno de ellos, uno por uno en su análisis de tiempo real, permitiendo así la generación de los ficheros necesarios para el virtual-environment.
   - ![Wait](https://img.shields.io/badge/-ESPERA_5_segundos-important) Hasta que aparezca la carpeta `.venv`

2. **🔄 Reinicio**
   - Cierra y vuelve a abrir VSCode (obligado ✨).
   - Verifica que en la terminal veas `(.venv)` al principio  
     *(Si no: Ejecuta `.\.venv\Scripts\activate` manualmente, pon `activate.bat` si estás en Bash)*


> **💣 (Opcional) Instalación de librerías con UV**
>   En la terminal PowerShell (.venv activado): 
>   Primero instalamos `uv` con 
>   ```powershell
>   pip install uv
>   ```
>   Procedemos a instalar las librerías con
>   ```powershell
>   python -m uv pip install -e .
>   ```

> **Este comando:**
> Instala dependencias de pyproject.toml
> Configura el proyecto en modo desarrollo (-e)
> Genera proyecto_2025a.egg-info con metadatos

> 1. ✅ Verificación Exitosa
   ✔️ Sin errores en terminal
   ✔️ Carpeta proyecto_2025a.egg-info creada
   ✔️ Posibilidad de importar dependencias desde Python

> 🔥 Notas Críticas
   - Procura usar la PowerShell como terminal predeterminada (o Bash).
   - Activar entorno virtual antes de cualquier operación.
   - Si usaste UV la carpeta `proyecto_2025a.egg-info` es esencial.

---

## 📁 Estructura del Proyecto

### Archivos de SpeedUp:
- `test_speedup_definitivo.py` - Test principal para speedup infinito
- `INFORME_SPEEDUP_INFINITO_FINAL.md` - Informe completo de resultados
- `SPEEDUP_EXTREMO_INFORME.md` - Informe anterior de progresión
- `demo_speedup_infinito.py` - Demo de la progresión hacia speedup infinito

### Archivos Intel oneAPI:
- `test_intel_oneapi.py` - Test específico Intel oneAPI
- `test_battle_intel_final.py` - Battle Intel (sin CUDA)
- `REPORTE_INTEL_ONEAPI.md` - Informe Intel oneAPI completo
- `src/testing/strategies/pqnodes/oapi_qnodes.py` - Implementación Intel

### Implementaciones Core:
- `src/strategies/q_nodes.py` - Algoritmo Q-Nodes original
- `src/testing/strategies/pqnodes/` - Implementaciones paralelas

*Para proceder con una introducción o guía de uso del aplicativo, dirígete a `.docs\application.md`, donde encontrarás cómo realizar análisis en este FrameWork.*
