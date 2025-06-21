from src.controllers.manager import Manager

# Importación de estrategias #
from src.strategies.force import BruteForce
from src.strategies.q_nodes import QNodes


def iniciar():
    """Punto de entrada"""
                    # ABCD #
    estado_inicial = "111111111111111"
    condiciones =    "111111111111111"
    alcance =        "111111111111111"
    mecanismo =      "111111111111111"

    gestor_redes = Manager(estado_inicial)
    tpm = gestor_redes.cargar_red()

    ### Ejemplo de solución mediante módulo de fuerza bruta ###
    analizador_bf = QNodes(tpm)

    sia_cero = analizador_bf.aplicar_estrategia(
        estado_inicial,
        condiciones,
        alcance,
        mecanismo,
    )
    print(sia_cero)
