from src.controllers.manager import Manager

# 👇 Importación de estrategias 👇 #
from src.strategies.force import BruteForce


def iniciar():
    """Punto de entrada"""
                    # ABCD #
    estado_inicial = "10000000"
    condiciones =    "11111110"
    alcance =        "11111110"
    mecanismo =      "11111110"

    gestor_redes = Manager(estado_inicial)
    tpm = gestor_redes.cargar_red()

    ### Ejemplo de solución mediante módulo de fuerza bruta ###
    analizador_bf = BruteForce(tpm)

    sia_cero = analizador_bf.aplicar_estrategia(
        estado_inicial,
        condiciones,
        alcance,
        mecanismo,
    )
    print(sia_cero)
