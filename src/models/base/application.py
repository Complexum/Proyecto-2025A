from src.models.enums.temporal_emd import TimeEMD
from src.constants.base import ABC_START, ACTIVE, INACTIVE
from src.models.enums.distance import MetricDistance
from src.models.enums.notation import Notation


class Application:
    """
    La clase aplicación es un singleton utilizado para obtención y configuración de parámetros a lo largo del programa.

    Args:
    ----
        `semilla_numpy`: La semilla determinista para el generador de números aleatorios de numpy.
        pagina_red_muestra: La página de la red a mostrar. Esta permite que se seleccione el dataset correcto ubicado en `src/samples/` para la ejecución en pruebas y solución con estrategias. Evidentemente debía ser el número de Sheldon.
        `distancia_metrica`: La distancia métrica a usar, relevante para cuando se realizan cálculos con emd-causal.
        `indexado_llegada`: Los datasets tienen cada uno de sus registros indexados de una forma específica, si el dataset ya está indexado no hay necesidad de re-indexarlo para hacer su correcto uso. Por defecto los datasets ya están indexados en little-endian.
        `notacion_indexado`: La notación de indexado a usar. Esta notación es comparada con la de llegada para ver si se debe re-indexar el dataset.
        `tiempo_emd`: El tiempo de la emd a utilizar. Significa si se va a hacer uso de la emd para comparar cambios de presente a futuro (efecto) o presente a pasado (causal) e inclusive podrían operarse ambos tiempos (información integrada).
        `modo_estados`: El modo de estados a usar. Como se aprecia los datasets sólo requieren asociar una columna con una variable en el tiempo `t+1`/`t-1`, no obstante esta columna es una reducción puesto es tomar la medición en cuanto a la probabilidad de encontrarse activo, no hace falta asociar la columna con la probabilidad de estar inactivo para el siguiente/previo tiempo (`t±1`) pues es redundante por complementariedad.
        `profiler_habilitado`: Si el profiler está habilitado, se almacenarán en `../../../review/profiling/` las vistas con tiempos y costes de la ejecución de un algoritmo específico que se haya querido medir.
    """

    def __init__(self) -> None:
        self.semilla_numpy = 73
        self.pagina_red_muestra: str = ABC_START
        self.distancia_metrica: str = MetricDistance.HAMMING.value
        self.indexado_llegada: str = Notation.LIL_ENDIAN.value
        self.notacion_indexado: str = Notation.LIL_ENDIAN.value
        self.tiempo_emd: str = TimeEMD.EMD_EFECTO.value
        self.modo_estados: bool = ACTIVE
        self.profiler_habilitado: bool = True

    def set_pagina_red_muestra(self, pagina: str):
        self.pagina_red_muestra = pagina

    def set_notacion(self, tipo: Notation):
        self.notacion_indexado = tipo

    def set_distancia(self, tipo: MetricDistance):
        self.distancia_metrica = tipo

    def set_estados_activos(self):
        self.modo_estados = ACTIVE

    def set_estados_inactivos(self):
        self.modo_estados = INACTIVE

    def set_tiempo_emd(self, tipo: TimeEMD):
        self.tiempo_emd = tipo

    def set_distancia_metrica(self, tipo: MetricDistance):
        self.distancia_metrica = tipo

    def activar_profiling(self) -> None:
        self.profiler_habilitado = True

    def desactivar_profiling(self) -> None:
        self.profiler_habilitado = False


aplicacion = Application()
