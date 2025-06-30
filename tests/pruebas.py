import numpy as np

from src.funcs.iit import ABECEDARY


def generar_subarreglos(arr):
    return [
        arr,  # 1. Todo el arreglo original
        arr[:-1],  # 2. Excluir el último elemento
        arr[1:],  # 3. Excluir el primer elemento
        arr[1:-1],  # 4. Excluir los extremos
        np.delete(arr, np.arange(2, len(arr), 3)),  # 5. Omitir múltiplos de 3
        arr[::2],  # 6. Tomar los elementos en posiciones pares
        arr[1::2],  # 7. Tomar los elementos en posiciones impares
    ]


num_nodos = 20
variables = range(num_nodos)

pruebas = []
pruebas_literales = []


for futuro in generar_subarreglos(variables):
    conjunto = []
    conjunto_literales = []

    futuro = set(futuro)
    for presente in generar_subarreglos(variables):
        # Para vista binaria
        presente = set(presente)
        bits_alcance = "".join(["1" if j in futuro else "0" for j in variables])
        bits_mecanismo = "".join(["1" if i in presente else "0" for i in variables])
        conjunto.append((bits_alcance, bits_mecanismo))
        ...
        literales_alcance = "".join([ABECEDARY[i] for i in futuro])
        literales_mecanismo = "".join([ABECEDARY[j] for j in presente])
        conjunto_literales.append((literales_alcance, literales_mecanismo))

    pruebas.append(conjunto)
    pruebas_literales.append(conjunto_literales)


def empezar_pruebitas():
    for conjunto, conjunto_literales in zip(pruebas, pruebas_literales):
        # print(conjunto)
        # print(conjunto_literales)
        # print(conjunto)
        for tupla in conjunto_literales:
            print(tupla[1])
