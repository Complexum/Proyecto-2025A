import time
from src.models.strategies.force import BruteForce
from src.controllers.manager  import Manager
from src.models.strategies.phi import Phi
from src.models.strategies.q_nodes import QNodes
import numpy as np
import pandas as pd

#----------------------------------------------------------------------------------
#                ESTRATEGIA Q  
# ---------------------------------------------------------------------------------

# def iniciar():
#     # """Punto de entrada principal"""

#     estado_inicio = "100000000000000" # Estado inicial del sistema
#     condiciones = "111111111111111"  # Sistema candidato
    
#     alcance = "110110110110110" # Futuro
    
#     num_nodos = len(estado_inicio)
#     variables = range(num_nodos)

#     config_sistema = Manager(estado_inicial=estado_inicio)

#     archivo_excel = "datosB.xlsx"
#     col_particion = "Partición"
#     col_perdida = "Pérdida"
#     col_tiempo = "Tiempo ejecución"

#     try:
#         df_existente = pd.read_excel(archivo_excel)
#     except FileNotFoundError:
#         df_existente = pd.DataFrame(columns=[col_particion, col_perdida, col_tiempo])

#     pruebas = []
#     i = 42

#     for presente in generar_subarreglos(variables):
#         # Para vista binaria
#         presente = set(presente)
#         bits_mecanismo = "".join(["1" if i in presente else "0" for i in variables])
#         pruebas.append(bits_mecanismo)

#     for mecanismo in pruebas:
#         i += 1
#         print(i)
#         print(f"{alcance=} {mecanismo=}")
#         analizador_Q = QNodes(config_sistema)
#         sia_dos = analizador_Q.aplicar_estrategia(condiciones, alcance, mecanismo)
#         print("Partición")
#         print(sia_dos.particion)
#         print("Perdida: ")
#         print(sia_dos.perdida)
#         print("Tiempo de ejecución: ")
#         print(sia_dos.tiempo_ejecucion)

#         lineas = sia_dos.particion.split("\n")

#         fila1 = pd.DataFrame(
#             [[lineas[0], sia_dos.perdida, sia_dos.tiempo_ejecucion]],
#             columns=[col_particion, col_perdida, col_tiempo],
#         )
#         fila2 = pd.DataFrame(
#             [[lineas[1], "", ""]],
#             columns=[col_particion, col_perdida, col_tiempo],
#         )

#         # Concatenar los nuevos datos con los existentes
#         df_existente = pd.concat([df_existente, fila1, fila2], ignore_index=True)

#         # Guardar el DataFrame actualizado en el archivo Excel
#         df_existente.to_excel(archivo_excel, index=False, engine="openpyxl")

#     # print(f"Datos guardados en {archivo_excel}")

# def generar_subarreglos(arr):
#     return [
#         arr,  # 1. Todo el arreglo original
#         arr[:-1],  # 2. Excluir el último elemento
#         arr[1:],  # 3. Excluir el primer elemento
#         arr[1:-1],  # 4. Excluir los extremos
#         arr[::2],  # 5. Tomar los elementos en posiciones pares
#         arr[1::2],  # 6. Tomar los elementos en posiciones impares
#         np.delete(
#             arr, np.arange(2, len(arr), 3)
#         ),  # 7. Omitir los múltiplos de 3 (índices)
#     ]


#----------------------------------------------------------------------------------
#                ESTRATEGIA PHI  
# ---------------------------------------------------------------------------------

# def iniciar():
#     # """Punto de entrada principal"""

#     estado_inicio = "100000000000000" # Estado inicial del sistema
#     condiciones = "111111111111111"  # Sistema candidato
    
#     alcance = "111111111111111" # Futuro
    
#     num_nodos = len(estado_inicio)
#     variables = range(num_nodos)

#     config_sistema = Manager(estado_inicial=estado_inicio)

#     archivo_excel = "datosB.xlsx"
#     col_particion = "Partición"
#     col_perdida = "Pérdida"
#     col_tiempo = "Tiempo ejecución"

#     try:
#         df_existente = pd.read_excel(archivo_excel)
#     except FileNotFoundError:
#         df_existente = pd.DataFrame(columns=[col_particion, col_perdida, col_tiempo])

#     pruebas = []
#     i = 42

#     for presente in generar_subarreglos(variables):
#         # Para vista binaria
#         presente = set(presente)
#         bits_mecanismo = "".join(["1" if i in presente else "0" for i in variables])
#         pruebas.append(bits_mecanismo)

#     for mecanismo in pruebas:
#         i += 1
#         print(i)
#         print(f"{alcance=} {mecanismo=}")
#         analizador_Phi = Phi(config_sistema)
#         sia_dos = analizador_Phi.aplicar_estrategia(condiciones, alcance, mecanismo)
#         print("Partición")
#         print(sia_dos.particion)
#         print("Perdida: ")
#         print(sia_dos.perdida)
#         print("Tiempo de ejecución: ")
#         print(sia_dos.tiempo_ejecucion)

#         lineas = sia_dos.particion.split("\n")

#         fila1 = pd.DataFrame(
#             [[lineas[0], sia_dos.perdida, sia_dos.tiempo_ejecucion]],
#             columns=[col_particion, col_perdida, col_tiempo],
#         )
#         fila2 = pd.DataFrame(
#             [[lineas[1], "", ""]],
#             columns=[col_particion, col_perdida, col_tiempo],
#         )

#         # Concatenar los nuevos datos con los existentes
#         df_existente = pd.concat([df_existente, fila1, fila2], ignore_index=True)

#         # Guardar el DataFrame actualizado en el archivo Excel
#         df_existente.to_excel(archivo_excel, index=False, engine="openpyxl")

#     # print(f"Datos guardados en {archivo_excel}")


# def generar_subarreglos(arr):
#     return [
#         arr,  # 1. Todo el arreglo original
#         arr[:-1],  # 2. Excluir el último elemento
#         arr[1:],  # 3. Excluir el primer elemento
#         arr[1:-1],  # 4. Excluir los extremos
#         arr[::2],  # 5. Tomar los elementos en posiciones pares
#         arr[1::2],  # 6. Tomar los elementos en posiciones impares
#         np.delete(
#             arr, np.arange(2, len(arr), 3)
#         ),  # 7. Omitir los múltiplos de 3 (índices)
#     ]


#----------------------------------------------------------------------------------
#                CÓDIGO ORIGINAL 
# ---------------------------------------------------------------------------------

from src.controllers.manager import Manager

from src.models.strategies.force import BruteForce

def iniciar():
    """Punto de entrada principal"""
                   # ABCD #
    estado_inicio = "100000000000000"
    condiciones =   "111111111111111"
    alcance =       "111111111111111"
    mecanismo =     "010101010101010"

    config_sistema = Manager(estado_inicial=estado_inicio)

    print(f'{config_sistema.pagina=}')
    

    ### Ejemplo de solución mediante módulo de fuerza bruta ###
    analizador_fb = Phi(config_sistema)
    sia_uno = analizador_fb.aplicar_estrategia(condiciones, alcance, mecanismo)
    print(sia_uno)
