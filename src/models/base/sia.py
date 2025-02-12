from abc import ABC, abstractmethod
import time

import numpy as np
import numpy.typing as NDArray

from src.middlewares.slogger import SafeLogger
from src.controllers.manager import Manager
from src.models.core.system import System

from src.constants.base import COLON_DELIM, FLOAT_ZERO, STR_ZERO


class SIA(ABC):
    """
    La clase SIA es la encargada de albergar como madre todos los diferentes algoritmos desarrollados, planteando la base de la que con el método `preparar_subsistema` se obtendrá uno con características indicadas por el usuario.

    Args:
    ----
        - config (Loader): El cargador de la data desde las muestras con las matrices, es relevante recordar que este tiene el estado inicial como cadena, por lo que es crucial su transoformación a `np.array(...)` para capacidad de indexar datos.
        - `sia_debug_observer` (DebugObserver): Debugger que no afecte el rendimiento de la ejecución para un sistema.
        - `sia_logger` (Logger): Imprime datos de la ejecución en `logs/<fecha>/<hora>/` asociando una hora específica por cada fecha del año, allí agrupa el resultado de la ejecución de los distintos loggers situados en aplicativo. De esta forma por hora se almacenará el último resultado de la ejecución.
        - `sia_subsistema` (System): El subsistema resultante de la preparación, es almacenado para tener una copia reutilizable en el proceso de particionamiento.
        - `sia_dists_marginales` (np.ndarray): Igualmente, una copia con fines de reutilización durante cálculos con la EMD.
    """

    def __init__(self, config: Manager) -> None:
        self.sia_loader = config
        self.sia_logger = SafeLogger("sia_preparation")

        self.sia_subsistema: System
        self.sia_dists_marginales: NDArray[np.float32]
        self.sia_tiempo_inicio: float = FLOAT_ZERO

    @abstractmethod
    def aplicar_estrategia(self):
        """
        Método principal sobre el que las clases herederas implementarán su algoritmo de resolución del problema con una metodología determinada.
        """

    def sia_cargar_tpm(self) -> np.ndarray:
        """Carga TPM desde archivo"""
        return np.genfromtxt(self.sia_loader.tpm_filename, delimiter=COLON_DELIM)

    def sia_preparar_subsistema(
        self,
        condicion: str,
        alcance: str,
        mecanismo: str,
    ):
        """Es en este método donde dada la entrada del usuario, vamos a generar un sistema completo, aplicamos condiciones de fondo (background conditions), loe substraemos partes para dejar un subsistema y es este el que retornamos pues este es el mínimo "sistema" útil para poder encontrar la bipartición que le genere la menor pérdida.

        Args:
            - `condicion` (str): Cadena de bits donde los bits en cero serán las dimensiones a condicionar.
            - `alcance` (str): Cadena de bits donde los bits en cero serán las dimensiones a substraer del alcance .
            - `mecanismo` (str): Cadena de bits donde los bits en cero serán las dimensiones a substraer del mecanismo.

        Raises:
            - `Exception:` Es crucial que todos tengan el mismo tamaño del estado inicial para correctamente identificar los índices y valor de cada variable rápidamente.
        """
        if self.chequear_parametros(condicion, alcance, mecanismo):
            raise Exception("Different cand and initial state size")

        dims_condicionadas = np.array(
            [ind for ind, bit in enumerate(condicion) if bit == STR_ZERO], dtype=np.int8
        )
        dims_alcance = np.array(
            [ind for ind, bit in enumerate(alcance) if bit == STR_ZERO], dtype=np.int8
        )
        dims_mecanismo = np.array(
            [ind for ind, bit in enumerate(mecanismo) if bit == STR_ZERO], dtype=np.int8
        )

        # Preparar directorio de salida
        self.sia_loader.output_dir.mkdir(parents=True, exist_ok=True)

        # Cargar y preparar datos
        tpm = self.sia_cargar_tpm()
        estado_inicial = np.array(
            [canal for canal in self.sia_loader.estado_inicial], dtype=np.int8
        )

        # Formación de datos con logs opcionales de ejemplificación
        completo = System(tpm, estado_inicial)
        # self.sia_logger.critic("Original:")
        # self.sia_logger.info(completo)

        candidato = completo.condicionar(dims_condicionadas)
        # self.sia_logger.warn("Candidato:")
        # self.sia_logger.info(f"{dims_condicionadas}")
        # self.sia_logger.debug(candidato)

        subsistema = candidato.substraer(dims_alcance, dims_mecanismo)
        # self.sia_logger.warn("Subsys:")
        # self.sia_logger.debug(f"{dims_alcance, dims_mecanismo=}")
        # self.sia_logger.error(subsistema)

        self.sia_subsistema = subsistema
        self.sia_dists_marginales = subsistema.distribucion_marginal()
        self.sia_tiempo_inicio = time.time()

    def chequear_parametros(self, candidato: str, futuro: str, presente: str):
        return not (
            len(self.sia_loader.estado_inicial)
            == len(candidato)
            == len(futuro)
            == len(presente)
        )
