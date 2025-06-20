from src.models.enums.temporal_emd import TemporalEMD
from src.constants.base import ABC_START, ACTIVE, INACTIVE
from src.models.enums.distance import MetricDistance
from src.models.enums.notation import Notation


class Application:
    """
    La clase aplicación es un singleton utilizado para obtención y configuración de parámetros a lo largo del programa.
    """

    def __init__(self) -> None:
        self.semilla_numpy = 73
        self.pagina_red_muestra: str = ABC_START
        self.distancia_metrica: str = MetricDistance.HAMMING.value
        self.indexado_llegada: str = Notation.LIL_ENDIAN.value
        self.notacion_indexado: str = Notation.LIL_ENDIAN.value
        self.tiempo_emd: str = TemporalEMD.EMD_EFECTO.value
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

    def set_tiempo_emd(self, tipo: TemporalEMD):
        self.tiempo_emd = tipo

    def set_distancia_metrica(self, tipo: MetricDistance):
        self.distancia_metrica = tipo

    def activar_profiling(self) -> None:
        self.profiler_habilitado = True

    def desactivar_profiling(self) -> None:
        self.profiler_habilitado = False


aplicacion = Application()
