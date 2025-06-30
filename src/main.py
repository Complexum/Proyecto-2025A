from src.controllers.manager import Manager

# 👇 Importación de estrategias 👇 #
from tests.pruebas import empezar_pruebitas

from src.strategies.force import BruteForce


def iniciar():
    """Punto de entrada"""
    empezar_pruebitas()

    # # ABCD #
    # estado_inicial = "1000"
    # condiciones =    "1110"
    # alcance =        "1110"
    # mecanismo =      "1110"

    # gestor_redes = Manager(estado_inicial)
    # mpt = gestor_redes.cargar_red()

    # ### Ejemplo de solución mediante módulo de fuerza bruta ###
    # analizador_bf = BruteForce(mpt)

    # sia_cero = analizador_bf.aplicar_estrategia(
    #     estado_inicial,
    #     condiciones,
    #     alcance,
    #     mecanismo,
    # )
    # print(sia_cero)
