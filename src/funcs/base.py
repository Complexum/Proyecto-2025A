from itertools import product
import logging
from datetime import datetime
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from pyemd import emd

from src.models.enums.distance import MetricDistance
from src.models.enums.notation import Notation

from src.models.base.application import aplicacion
from src.constants.base import ABC_START, INT_ZERO


# @cache
def get_labels(n: int) -> tuple[str, ...]:
    def get_excel_column(n: int) -> str:
        if n <= 0:
            return ""
        return get_excel_column((n - 1) // 26) + chr((n - 1) % 26 + ord(ABC_START))

    return tuple([get_excel_column(i) for i in range(1, n + 1)])


ABECEDARY = get_labels(40)
LOWER_ABECEDARY = [letter.lower() for letter in ABECEDARY]


def literales(remaining_vars: NDArray[np.int8], lower: bool = False):
    return (
        "".join(ABECEDARY[i].lower() if lower else ABECEDARY[i] for i in remaining_vars)
        if remaining_vars.size
        else "∅"
    )


def seleccionar_metrica(distancia_usada: str):
    distancias_metricas = {
        MetricDistance.EMD_EFECTO.value: emd_efecto,
        MetricDistance.EMD_CAUSA.value: emd_causal,
        # ...otras
    }
    return distancias_metricas[distancia_usada]


def emd_efecto(u: NDArray[np.float32], v: NDArray[np.float32]) -> float:
    """
    Solución analítica de la Earth Mover's Distance basada en variables independientes condicionalmente.
    Sean X_1, X_2 dos variables aleatorias con su correspondiente espacio de estados. Si X_1 y X_2 son independientes y u_1, v_1 dos distribuciones de probabilidad en X_1 y u_2, v_2 dos distribuciones de probabilidad en X_2.

    Args:
        u (NDArray[np.float32]): Histograma/distribución/vector/serie donde cada indice asocia un valor de pobabilidad de tener el nodo en estado OFF.
        v (NDArray[np.float32]): Histograma/distribución/vector/serie donde cada indice asocia un valor de pobabilidad de tener el nodo en estado OFF.

    Returns:
        float: La EMD entre los repertorios efecto es igual a la suma entre las EMD de las distribuciones marginales de cada nodo, de forma que la EMD entre las distribuciones marginales para un nodo es la diferencia absoluta entre las probabilidades con el nodo OFF.
    """
    return np.sum(np.abs(u - v))


def emd_causal(u: NDArray[np.float64], v: NDArray[np.float64]) -> float:
    """
    Calculate the Earth Mover's Distance (EMD) between two probability distributions u and v.
    The Hamming distance was used as the ground metric.
    """
    if not all(isinstance(arr, np.ndarray) for arr in [u, v]):
        raise TypeError("u and v must be numpy arrays.")

    n: int = u.size
    costs: NDArray[np.float64] = np.empty((n, n))

    for i in range(n):
        # Utiliza comprensión de listas para calcular los costos
        costs[i, :i] = [hamming_distance(i, j) for j in range(i)]
        costs[:i, i] = costs[i, :i]  # Reflejar los valores
    np.fill_diagonal(costs, INT_ZERO)

    cost_mat: NDArray[np.float64] = np.array(costs, dtype=np.float64)
    return emd(u, v, cost_mat)


def hamming_distance(a: int, b: int) -> int:
    return count_bits(a ^ b)


def count_bits(n: int) -> int:
    return bin(n).count("1")


def reindexar(N: int):
    notaciones = {
        Notation.BIG_ENDIAN.value: big_endian(N),
        Notation.LIL_ENDIAN.value: lil_endian(N),
        # ...otras
    }
    return notaciones[aplicacion.notacion]


def seleccionar_estado(subestado: np.ndarray) -> np.ndarray:
    # posible in-deducción por acceso inverso
    notaciones = {
        Notation.BIG_ENDIAN.value: subestado,
        Notation.LIL_ENDIAN.value: subestado[::-1],
        # ...otras
    }
    return notaciones[aplicacion.notacion]


def count_bits(n: int) -> int:
    return bin(n).count("1")


def big_endian(n: int) -> np.ndarray:
    return np.array(range(n), dtype=np.uint32)


def lil_endian(n: int) -> np.ndarray:
    """
    Implementación final optimizada para generación de little endian.
    Combina las mejores prácticas encontradas en nuestras pruebas.
    """
    if n <= 0:
        return np.array([0], dtype=np.uint32)  # Caso especial para n=0

    size = 1 << n
    result = np.zeros(size, dtype=np.uint32)

    # Optimización de parámetros basada en n
    block_bits = max(12, min(16, 28 - int(np.log2(n))))
    block_size = 1 << block_bits

    # Precomputar shifts de una vez
    shifts = np.array([n - i - 1 for i in range(n)], dtype=np.uint32)

    # Pre-alocar buffer para procesamientos por bloque
    block_result = np.zeros(block_size, dtype=np.uint32)

    # Determinar tamaño óptimo de grupo de bits
    bit_group_size = 6 if n > 24 else 4  # Ajuste basado en pruebas empíricas

    for start in range(0, size, block_size):
        end = min(start + block_size, size)
        current_size = end - start

        # Reset eficiente del buffer
        block_result[:current_size] = 0
        block_indices = np.arange(start, end, dtype=np.uint32)

        # Procesar bits en grupos optimizados
        for base_bit in range(0, n, bit_group_size):
            bits_remaining = min(bit_group_size, n - base_bit)
            if bits_remaining <= 0:
                break

            # Optimización: procesamiento de múltiples bits de una vez
            group_mask = np.uint32((1 << bits_remaining) - 1)
            group_values = (block_indices >> base_bit) & group_mask

            for j in range(bits_remaining):
                shift = shifts[base_bit + j]
                bit_value = (group_values >> j) & np.uint32(1)
                block_result[:current_size] |= bit_value << shift

        result[start:end] = block_result[:current_size]

    return result


def get_restricted_combinations(binary_str: str) -> tuple[list[str], list[str]]:
    """
    Genera las combinaciones para B y C basadas en la cadena binaria A.
    B solo puede tener 1s donde A tiene 1s.
    """
    # Contar cuántos 1s hay en la cadena
    ones_count = binary_str.count("1")
    width = len(binary_str)

    # Encontrar las posiciones de los 1s en A
    one_positions = [i for i, bit in enumerate(binary_str) if bit == "1"]

    def generate_valid_combinations():
        # Generamos todas las combinaciones posibles de 0s y 1s para las posiciones donde A tiene 1s
        base_combinations = list(product(["0", "1"], repeat=ones_count))
        valid_combinations = []

        # Para cada combinación base, creamos una cadena del ancho total
        for comb in base_combinations:
            # Empezamos con todos 0s
            result = ["0"] * width
            # Colocamos los bits de la combinación en las posiciones donde A tiene 1s
            for pos, bit in zip(one_positions, comb):
                result[pos] = bit
            valid_combinations.append("".join(result))

        return valid_combinations

    # B tiene restricciones, C no
    B = generate_valid_combinations()
    C = (
        B.copy()
    )  # En este caso C es igual a B, pero podría ser diferente si se necesita

    return B, C


def generate_combinations(A: str) -> list[tuple[str, str, str]]:
    """
    Genera el producto cartesiano final de A con las combinaciones válidas de B y C.
    """
    B, C = get_restricted_combinations(A)
    # Convertimos A, B y C en formato "XX XX XX"
    formatted_B = ["".join(b[i : i + 2] for i in range(0, len(b), 2)) for b in B]
    formatted_C = ["".join(c[i : i + 2] for i in range(0, len(c), 2)) for c in C]
    formatted_A = "".join(A[i : i + 2] for i in range(0, len(A), 2))

    # Generamos el producto cartesiano
    return list(product([formatted_A], formatted_B, formatted_C))[1:]


def dec2bin(decimal: int, width: int) -> str:
    return format(decimal, f"0{width}b")


def estados_binarios(n: int):
    return [dec2bin(i, n) for i in range(1 << n)][1:]


# def estados_binarios(n: int, veces=3):
#     # Números de 0 a 2^N #
#     rango = [dec2bin(i, n) for i in range(2**n)]
#     return product(rango, repeat=veces)
