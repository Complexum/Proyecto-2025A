from src.controllers.manager import Manager
from src.controllers.strategies.force import BruteForce
from src.controllers.strategies.q_nodes import QNodes
from src.controllers.strategies.geometric import GeometricSIA


def iniciar():
    """Punto de entrada principal"""
                    # ABCD #
    estado_inicial = "100000000000000"  
    condiciones =    "111111111111111"
    alcance =        "011111111111111"
    mecanismo =      "010101010101010"

    gestor_sistema = Manager(estado_inicial)

    ### Ejemplo de solución mediante módulo de fuerza bruta ###
    analizador_fb = GeometricSIA(gestor_sistema)
    sia_uno = analizador_fb.aplicar_estrategia(
        condiciones,
        alcance,
        mecanismo,
    )
    print(sia_uno)
