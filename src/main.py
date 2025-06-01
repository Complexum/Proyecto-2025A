from src.controllers.manager import Manager

from src.controllers.strategies.phi import Phi
from src.controllers.strategies.force import BruteForce
from src.controllers.strategies.geometry import Geometry


def iniciar():
    """Punto de entrada principal"""
                    # ABCD #
    estado_inicial = "1000"
    condiciones =    "1110"
    alcance =        "1111"
    mecanismo =      "1111"

    gestor_sistema = Manager(estado_inicial)

    ### Ejemplo de solución mediante módulo de fuerza bruta ###
    analizador_phi = BruteForce(gestor_sistema)

    sia_cero = analizador_phi.aplicar_estrategia(
        condiciones,
        alcance,
        mecanismo,
    )

    print(sia_cero)
