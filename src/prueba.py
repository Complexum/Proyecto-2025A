import numpy as np
from src.controllers.manager import Manager

from src.controllers.strategies.geometry import Geometry


def iniciar():
    """Punto de entrada principal"""
                    # ABCD #
    estado_inicial = "100"
    condiciones =    "111"
    alcance =        "111"
    mecanismo =      "111"

    gestor_sistema = Manager(estado_inicial)

    ### Ejemplo de solución mediante módulo de fuerza bruta ###
    analizador_fb = Geometry(gestor_sistema)
    sia_uno = analizador_fb.aplicar_estrategia(
        condiciones,
        alcance,
        mecanismo,
    )
    print(sia_uno)

    # # leer el csv en la ruta `src\.samples\N10A.csv`
    # dataset = np.genfromtxt(
    #     r"src\.samples\N10A.csv",
    #     delimiter=",",
    #     dtype=str,
    # )
    # # sacar el promedio de las filas

    # dataset = np.mean(dataset, axis=0)
    # print(f"El promedio de las filas es: {dataset}")
