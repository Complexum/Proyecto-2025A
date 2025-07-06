### Ejecución del programa

Abres una terminal, escribes `py e` tabulas y das enter, _así de simple_! Alternativamente escribiendo en terminal `python .\exec.py` deberás ejecutar una muestra del aplicativo para una Red de 04 nodos, generarando un análisis completo sobre la misma, de tal forma que se obtendrán varios artefactos tras la ejecución.

Por otro lado puedes realizar un anális específico sobre una red usando el método `aplicar_estrategia(...)` con los parámetros respectivos.

Si te sale un error que esté asociado con las herramientas de desarrollo de c++, esto ocurre puesto Pyphi utiliza compiladores en Cython/C/C++ para el cálculo de la EMD Causal. Con esto debes debes instalar [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/es/visual-cpp-build-tools/), al abrirlo tendrás dos opciones, que ya esté configurado el instalador o que sea la primera vez, si ya lo tienes instalado dale en "Modificar", si no lo tienes entonces te saldrán las herramientas a utilizar, en ambos casos en este punto tendrás que seleccionar la primera opción para el desarrollo con C++, al clickearlo a la derecha habrás de seleccionar el checkbox con la opción `MSVCv142 - VS 2019 C++ x64/86 build tools`, tras instalado puedes reiniciar tu VSC y debería de arreglarse para siempre.

Al final podemos realizar ejecución desde `py exec` y pasar a corregir los errores de la librería Pyphi *(si usas una versión superior a python 3.9.13)* (en el documento `.docs\errors\with_pyphi.md` encuentras la guía de bolsillo para arreglar estos problemas).

> Si quisiéramos hacer una prueba con un subsistema **específico** para una red utilizando fuerza bruta, hacemos lo siguiente:

```py
from src.controllers.manager import Manager
from src.controllers.strategies.force import BruteForce


def iniciar():
    """Punto de entrada principal"""
                   # ABCD #
    estado_inicio = "1000"
    condiciones =   "1110"
    alcance =       "1110"
    mecanismo =     "1110"

    gestor_sistema = Manager(estado_inicial=estado_inicio)

    ### Ejemplo de solución mediante módulo de fuerza bruta ###
    analizador_fb = BruteForce(gestor_sistema)
    sia_uno = analizador_fb.aplicar_estrategia(condiciones, alcance, mecanismo)
    print(sia_uno)
```

Podemos ver cómo al definir el estado inicial `1000` estamos usando implícitamente una red de **04 Nodos** y sólo asignamos al primer nodo _(el A=1)_ el valor de 1 _(canal activo)_ y los demás _(BCD=000)_ o inactivos.

Estas redes estarán ubicadas en el directorio `.samples\`, si tenemos varias redes del mismo tamaño, podemos etiquetarlas como *"Network with 04 nodes, A"* o su abreviación *"N4A"*, tal que otra podría ser *"N4B"*, *"N4C"*, etc. Si queremos seleccionar entonces la red A, B o C deberemos configurar en el aplicativo cuál página querremos utilizar, esto es apreciable en `exec.py`, donde idealmente daremos estas configuraciones iniciales y serán extendidas a todo el aplicativo.

---

Por ejemplo, una ejecución con **Pyphi** para una red específica se vería así:

```py
from src.controllers.manager import Manager
from src.controllers.strategies.phi import Phi

def iniciar():
    """Punto de entrada principal"""
                   # ABCD #
    estado_inicio = "1000"
    condiciones =   "1110"
    alcance =       "1010"
    mecanismo =     "0110"

    gestor_sistema = Manager(estado_inicial=estado_inicio)

    ### Ejemplo de solución mediante Pyphi ###
    analizador_fi = Phi(gestor_sistema)
    sia_dos = analizador_fi.aplicar_estrategia(condiciones, alcance, mecanismo)
    print(sia_dos)
```

Donde sobre un sistema de nodos $V=\{A,B,C,D\}$ tomamos un sistema candidato $V_c=\{A,B,C\}$ subsistema, y en los tiempos $t_0=\{B,C\}$ y $t_1=\{A,C\}$, nótese cómo sólo en el subsistema se presenta temporalidad.

Como se aprecia, cada variable está asociada con una posición, de forma que las variables a **mantener** tienen el bit en uno (1), mientras que las que querremos **descartar** las enviaremos en cero (0).

---

#### Herramientas de diagnóstico

En este caso, lo que hacemos es ejecutar un análisis completo sobre una red, analizando todos sus posibles sistemas candidatos. Para cada uno de ellos, se evalúan sus posibles subsistemas y sobre cada uno se realiza un _Análisis de Irreducibilidad Sistémica_ (SIA), proporcionando tanto la solución de la ejecución como metadatos para un análisis más profundo.

Este resultado se ubicará en el directorio `review\resolver\red_ejecutada\estado_inicial\`, donde:
- Cada sistema candidato será un archivo Excel.
- Cada hoja representará un posible subsistema.
- Cada fila mostrará una partición de las variables en tiempo presente $(t_0)$.
- Las columnas indicarán el estado en un tiempo futuro $(t_1)$.

Además, se cuenta con un decorador `@profile` en `src.middlewares.profile`, aplicable sobre cualquier función. Este decorador permite generar un análisis temporal del llamado de subrutinas, con dos modos de visualización: una vista global _(Call Stack)_ y una vista particular _(Timeline)_. Esto será útil para la detección de **cuellos de botella** y la optimización del programa.

Adicionalmente, en el directorio `logs`, cada vez que se use `self.logger` en la clase de ejecución, se generará un archivo con los datos logeados. Estos se almacenan por carpetas con la estructura `dia_mes_año\hora\metodo_del_log`, lo que permite un seguimiento detallado de la ejecución. Este logger se vuelve especialmente útil cuando los rastros de ejecución son extremadamente extensos.

---

Si deseas realizar un análisis completo de una red mediante fuerza bruta, puedes hacerlo con el siguiente código:

```py
from src.controllers.manager import Manager
from src.controllers.strategies.force import BruteForce

def iniciar():
    """Punto de entrada principal"""
                   # ABCD #
    estado_inicio = "1000"
    gestor_sistema = Manager(estado_inicial=estado_inicio)

    ## Ejemplo de solución mediante fuerza bruta ##
    analizador_fb = BruteForce(gestor_sistema)
    analizador_fb.analizar_completamente_una_red()
```

---

### Pruebas 🧪

En el archivo de pruebas en el directorio `.tests` encontrarás el documento excel con las pruebas a resolver mediante uso del aplicativo.

Si deseas realizar pruebas con una matriz superior a las ya diseñadas, puedes hacer uso del `Manager` para generar una nueva, de forma tal que usando su método `generar_red(dimensiones: int)` quedará almacenada en el directorio de samples para su uso posterior.

Para finalizar cabe recordar que el repositorio está atento a cambios o mejoras propuestas por parte de los cursantes, de forma que es oportuno realizar `git pull origin main` para tener siempre la versión más reciente 🫶!