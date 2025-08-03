from abc import ABC, abstractmethod
import time

import numpy as np
import numpy.typing as NDArray

from src.constants.models import SIA_PREPARATION_TAG
from src.middlewares.slogger import SafeLogger
from src.models.core.system import System

from src.constants.base import (
    COLS_IDX,
    FLOAT_ZERO,
    STR_ZERO,
)
from src.constants.error import (
    ERROR_ESPACIOS_INCOMPATIBLES,
)


class SIA(ABC):
    """
    La clase SIA es la encargada de albergar como madre todos los diferentes algoritmos desarrollados, planteando la base de la que con el método `preparar_subsistema` se obtendrá uno con características indicadas por el usuario.

    Args:
    ----
        - `sia_gestor` (Manager): El gestor de la data desde las muestras con las matrices, es relevante recordar que este tiene el estado inicial como cadena, por lo que es crucial su transoformación a `np.array(...)` para capacidad de indexar datos.
        - `sia_logger` (SafeLogger): Imprime datos de la ejecución en `logs/<fecha>/<hora>/` asociando una hora específica por cada fecha del año, allí agrupa el resultado de la ejecución de los distintos loggers situados en aplicativo. De esta forma por hora se almacenará el último resultado de la ejecución.
        - `sia_subsistema` (System): El subsistema resultante de la preparación, es almacenado para tener una copia reutilizable en el proceso de particionamiento.
        - `sia_dists_marginales` (np.ndarray): Igualmente, una copia con fines de reutilización durante cálculos con la EMD.
        - `sia_tiempo_inicio` (float): Tiempo de inicio de la ejecución.
    """

    def __init__(self, tpm: np.ndarray) -> None:
        self.tpm = tpm
        self.sia_logger = SafeLogger(SIA_PREPARATION_TAG)

        self.sia_subsistema: System
        self.sia_dists_marginales: NDArray[np.float32]
        self.sia_tiempo_inicio: float = FLOAT_ZERO
        self.memoria_candidato: System = None

    @abstractmethod
    def aplicar_estrategia(self):
        """
        Método principal sobre el que las clases herederas implementarán su algoritmo de resolución del problema con una metodología determinada.
        """

    def sia_preparar_subsistema(
        self,
        estado_inicial: str,
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
        if self.chequear_parametros(estado_inicial, condicion, alcance, mecanismo):
            raise SystemError(ERROR_ESPACIOS_INCOMPATIBLES)

        if self.memoria_candidato is None:
            dims_condicionadas = np.array(
                [ind for ind, bit in enumerate(condicion) if bit == STR_ZERO],
                dtype=np.int8,
            )

            dims_estado_inicial = np.array(
                [int(ind) for ind in estado_inicial],
                dtype=np.int8,
            )
            completo = System(self.tpm, dims_estado_inicial)
            # self.sia_logger.critic("Original creado.")
            # self.sia_logger.info(completo)
            # self.sia_logger.critic("Original:")
            # self.sia_logger.info(completo)

            candidato = completo.condicionar(dims_condicionadas)
            # self.sia_logger.critic("Sisema Candidato creado.")
            # self.sia_logger.warn(f"{dims_condicionadas}")
            # self.sia_logger.debug(candidato)

            self.memoria_candidato = candidato
        else:
            candidato = self.memoria_candidato

        dims_alcance = np.array(
            [ind for ind, bit in enumerate(alcance) if bit == STR_ZERO],
            dtype=np.int8,
        )
        dims_mecanismo = np.array(
            [ind for ind, bit in enumerate(mecanismo) if bit == STR_ZERO],
            dtype=np.int8,
        )

        subsistema = candidato.substraer(dims_alcance, dims_mecanismo)
        subsistema.limpiar_memorandos()
        self.sia_logger.critic("Subsistema creado.")
        # self.sia_logger.debug(f"{dims_alcance, dims_mecanismo=}")
        # self.sia_logger.debug(subsistema)

        self.sia_subsistema = subsistema
        self.sia_dists_marginales = subsistema.distribucion_marginal()
        self.sia_tiempo_inicio = time.time()

    def chequear_parametros(
        self, estado_inicial: str, candidato: str, futuro: str, presente: str
    ):
        """Valida que los datos enviados por el usuario sean correctos, donde no hay problema si tienen la misma longitud puesto se están asignando los valores correspondientes a cada variable.

        Args:
            `candidato` (str): Cadena de texto que representa la presencia o ausencia de un conjunto de variables que serán enviadas para condicionar el sistema original dejándolo como un Sistema candidato, si su bit asociado equivale a 0 se condiciona la variable, si equivale a 1 esta variable se mantendrá en el sistema durante toda la ejecución (hasta que un subsistema la marginalice).
            `futuro` (str): Cadena de texto que representa la presencia o ausencia de un conjunto de variables que serán enviadas para substraer en el alcance del Sistema candidato dejándo un Subsistema, si su bit asociado equivale a 0 la variable será marginalizada, si equivale a 1 la variable se mantendrá en el Sistema candidato durante toda la ejecución (hasta que una partición la marginalice).
            `presente` (str): Cadena de texto que representa la presencia o ausencia de un conjunto de variables que serán enviadas para substraer en el mecanismo del Sistema candidato dejándolo como un Subsistema, si su bit asociado equivale a 0 la variable será marginalizada, si equivale a 1 la variable se mantendrá en el Sistema candidato durante toda la ejecución (hasta que una partición la marginalice).

        Returns:
            bool: True si las dimensiones son diferentes, de otra forma los parámetros enviados son válidos (y depende si existe la red asociada).
        """
        return not (
            len(self.tpm[COLS_IDX])
            == len(estado_inicial)
            == len(candidato)
            == len(futuro)
            == len(presente)
        )
