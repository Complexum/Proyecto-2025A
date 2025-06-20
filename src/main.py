from src.controllers.manager import Manager

# Importación de estrategias #
from src.strategies.force import BruteForce


def iniciar():
    """Punto de entrada"""
                    # ABCD #
    estado_inicial = "1000"
    condiciones =    "1110"
    alcance =        "1110"
    mecanismo =      "1110"

    gestor_redes = Manager(estado_inicial)

    ### Ejemplo de solución mediante módulo de fuerza bruta ###
    analizador_bf = BruteForce(gestor_redes)

    sia_cero = analizador_bf.aplicar_estrategia(
        condiciones,
        alcance,
        mecanismo,
    )
    print(sia_cero)
