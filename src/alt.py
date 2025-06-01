from constants.base import STR_ONE, STR_ZERO
from src.middlewares.slogger import SafeLogger

from src.testing.data import (
    NUM_NODOS,
    PRUEBAS,
    RED_05,
    RED_10,
    RED_15,
)
from src.constants.models import (
    QNODES_STRAREGY_TAG,
)

from src.controllers.manager import Manager
from src.controllers.strategies.phi import Phi

# En tu función principal:
from src.testing.result import GestorResultados  # Ajusta la ruta según tu estructura


def iniciar():
    """Punto de entrada principal"""
    red_usada = RED_10

    reactor = GestorResultados(
        num_nodos=red_usada[NUM_NODOS],
        strategy=QNODES_STRAREGY_TAG,
    )

    muestras: list[list[tuple[str, str]]] = red_usada[PRUEBAS]
    num_nodos: int = red_usada[NUM_NODOS]

    estado_inicio = f"{STR_ONE}{STR_ZERO * (num_nodos - 1)}"
    condiciones = STR_ONE * num_nodos

    config_sistema = Manager(estado_inicial=estado_inicio)
    logger_qnodes = SafeLogger(QNODES_STRAREGY_TAG)

    procesar_muestras(muestras, reactor, logger_qnodes, config_sistema, condiciones)


def procesar_muestras(
    muestras: list[list[tuple[str, str]]],
    reactor: GestorResultados,
    logger: SafeLogger,
    config_sistema: Manager,
    condiciones: str,
) -> None:
    ...
    for lote in muestras:
        for prueba in lote:
            # Verificamos si ya existe el resultado
            if reactor.obtener_resultado(*prueba):
                continue

            logger.error(f"\n{prueba=}")
            alcance, mecanismo = prueba
            analizador_phi = Phi(config_sistema)

            solucion = analizador_phi.aplicar_estrategia(
                condiciones,
                alcance,
                mecanismo,
            )

            # Guardamos el resultado
            reactor.guardar_resultado(
                alcance=alcance,
                mecanismo=mecanismo,
                perdida=solucion.perdida,
                tiempo=solucion.tiempo_ejecucion,
            )
