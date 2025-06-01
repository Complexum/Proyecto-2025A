import time
from typing import Union
import numpy as np
from mpi4py import MPI
from src.middlewares.slogger import SafeLogger
from src.funcs.base import emd_efecto, ABECEDARY
from src.middlewares.profile import profiler_manager, profile
from src.funcs.format import fmt_biparte_q
from src.controllers.manager import Manager
from src.models.base.sia import SIA

from src.models.core.solution import Solution
from src.constants.models import (
    QNODES_ANALYSIS_TAG,
    QNODES_LABEL,
    QNODES_STRAREGY_TAG,
)
from src.constants.base import (
    TYPE_TAG,
    NET_LABEL,
    INFTY_NEG,
    INFTY_POS,
    LAST_IDX,
    EFECTO,
    ACTUAL,
)


class QNodes(SIA):
    """
    Clase QNodes para el análisis de redes mediante el algoritmo Q con paralelización MPI.

    Esta clase implementa un gestor principal para el análisis de redes que utiliza
    el algoritmo Q para encontrar la partición óptima que minimiza la
    pérdida de información en el sistema. Hereda de la clase base SIA (Sistema de
    Información Activo) y proporciona funcionalidades para analizar la estructura
    y dinámica de la red.

    La implementación utiliza MPI para paralelizar el ciclo más interno del algoritmo,
    donde se evalúan los deltas candidatos para combinar con el conjunto omega actual.
    """

    def __init__(self, gestor: Manager):
        super().__init__(gestor)
        # Inicializar MPI
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()

        profiler_manager.start_session(
            f"{NET_LABEL}{len(gestor.estado_inicial)}{gestor.pagina}"
        )
        self.m: int
        self.n: int
        self.tiempos: tuple[np.ndarray, np.ndarray]
        self.etiquetas = [tuple(s.lower() for s in ABECEDARY), ABECEDARY]
        self.vertices: set[tuple]
        # self.memoria_delta = dict()
        self.memoria_omega = dict()
        self.memoria_particiones = dict()

        self.indices_alcance: np.ndarray
        self.indices_mecanismo: np.ndarray

        self.logger = SafeLogger(QNODES_STRAREGY_TAG)

    @profile(context={TYPE_TAG: QNODES_ANALYSIS_TAG})
    def aplicar_estrategia(
        self,
        condicion: str,
        alcance: str,
        mecanismo: str,
    ):
        self.sia_preparar_subsistema(condicion, alcance, mecanismo)

        futuro = tuple(
            (EFECTO, efecto) for efecto in self.sia_subsistema.indices_ncubos
        )
        presente = tuple(
            (ACTUAL, actual) for actual in self.sia_subsistema.dims_ncubos
        )  #

        self.m = self.sia_subsistema.indices_ncubos.size
        self.n = self.sia_subsistema.dims_ncubos.size

        self.indices_alcance = self.sia_subsistema.indices_ncubos
        self.indices_mecanismo = self.sia_subsistema.dims_ncubos

        self.tiempos = (
            np.zeros(self.n, dtype=np.int8),
            np.zeros(self.m, dtype=np.int8),
        )

        vertices = list(presente + futuro)
        self.vertices = set(presente + futuro)
        mip = self.algorithm(vertices)

        fmt_mip = fmt_biparte_q(list(mip), self.nodes_complement(mip))
        perdida_mip, dist_marginal_mip = self.memoria_particiones[mip]

        return Solution(
            estrategia=QNODES_LABEL,
            perdida=perdida_mip,
            distribucion_subsistema=self.sia_dists_marginales,
            distribucion_particion=dist_marginal_mip,
            tiempo_total=time.time() - self.sia_tiempo_inicio,
            particion=fmt_mip,
        )

    def algorithm(self, vertices: list[tuple[int, int]]):
        """
        Implementa el algoritmo Q para encontrar la partición óptima utilizando MPI
        para paralelizar la evaluación de deltas candidatos.

        El proceso con rango 0 (proceso principal) coordina la delegación de tareas,
        mientras que los otros procesos realizan el cálculo de la función submodular
        para los deltas asignados.
        """
        omegas_origen = np.array([vertices[0]])
        deltas_origen = np.array(vertices[1:])

        vertices_fase = vertices

        omegas_ciclo = omegas_origen
        deltas_ciclo = deltas_origen

        total = len(vertices_fase) - 2
        for i in range(len(vertices_fase) - 2):
            if self.rank == 0:
                self.logger.debug(f"total: {total - i}")

            omegas_ciclo = [vertices_fase[0]]
            deltas_ciclo = vertices_fase[1:]

            emd_particion_candidata = INFTY_POS

            for j in range(len(deltas_ciclo) - 1):
                # Solo el proceso 0 (principal) controla el flujo general
                # emd_local = 1e5
                indice_mip = 0

                # Paralelización del ciclo interno (k)
                if self.rank == 0:
                    # Proceso principal: distribuye trabajo y recopila resultados

                    # Determinar número de deltas a evaluar por proceso
                    chunk_size = len(deltas_ciclo) // self.size
                    remainder = len(deltas_ciclo) % self.size

                    # Resultados para almacenar
                    all_results = []

                    # Distribuir trabajo a otros procesos
                    for p in range(1, self.size):
                        start_idx = p * chunk_size + min(p, remainder)
                        end_idx = (p + 1) * chunk_size + min(p + 1, remainder)

                        if start_idx < len(deltas_ciclo):
                            # Enviar índices y datos necesarios
                            work_indices = list(
                                range(start_idx, min(end_idx, len(deltas_ciclo)))
                            )
                            self.comm.send(
                                (work_indices, omegas_ciclo, deltas_ciclo),
                                dest=p,
                                tag=10,
                            )

                    # Proceso principal también hace su parte del trabajo
                    start_idx = 0
                    end_idx = chunk_size + min(1, remainder)

                    # Procesar la porción del proceso principal
                    for k in range(start_idx, min(end_idx, len(deltas_ciclo))):
                        emd_union, emd_delta, dist_marginal_delta = (
                            self.funcion_submodular(deltas_ciclo[k], omegas_ciclo)
                        )
                        emd_iteracion = emd_union - emd_delta
                        all_results.append(
                            (k, emd_iteracion, emd_delta, dist_marginal_delta)
                        )

                    # Recopilar resultados de otros procesos
                    for p in range(1, self.size):
                        process_results = self.comm.recv(source=p, tag=11)
                        if process_results:  # Si hay resultados de este proceso
                            all_results.extend(process_results)

                    # Encontrar el mejor resultado (menor EMD)
                    if all_results:
                        best_result = min(all_results, key=lambda x: x[1])
                        indice_mip = best_result[0]
                        emd_particion_candidata = best_result[2]
                        dist_particion_candidata = best_result[3]

                else:
                    # Procesos trabajadores: reciben datos y procesan
                    try:
                        work_data = self.comm.recv(source=0, tag=10)
                        if work_data:
                            work_indices, omegas_data, deltas_data = work_data
                            results = []

                            # Procesar los índices asignados
                            for k in work_indices:
                                emd_union, emd_delta, dist_marginal_delta = (
                                    self.funcion_submodular(deltas_data[k], omegas_data)
                                )
                                emd_iteracion = emd_union - emd_delta
                                results.append(
                                    (k, emd_iteracion, emd_delta, dist_marginal_delta)
                                )

                            # Enviar resultados al proceso principal
                            self.comm.send(results, dest=0, tag=11)
                    except Exception as e:
                        # Manejo de errores: enviar lista vacía en caso de error
                        self.logger.error(f"Error en proceso {self.rank}: {e}")
                        self.comm.send([], dest=0, tag=11)

                # Sincronizar todos los procesos antes de continuar
                self.comm.barrier()

                # Solo el proceso principal actualiza las estructuras de datos
                if self.rank == 0:
                    omegas_ciclo.append(deltas_ciclo[indice_mip])
                    deltas_ciclo.pop(indice_mip)

                # Broadcast de las nuevas estructuras para mantener sincronía
                omegas_ciclo = self.comm.bcast(omegas_ciclo, root=0)
                deltas_ciclo = self.comm.bcast(deltas_ciclo, root=0)

            # Solo el proceso principal actualiza la memoria de particiones
            if self.rank == 0:
                self.memoria_particiones[
                    tuple(
                        deltas_ciclo[LAST_IDX]
                        if isinstance(deltas_ciclo[LAST_IDX], list)
                        else deltas_ciclo
                    )
                ] = emd_particion_candidata, dist_particion_candidata

                par_candidato = (
                    [omegas_ciclo[LAST_IDX]]
                    if isinstance(omegas_ciclo[LAST_IDX], tuple)
                    else omegas_ciclo[LAST_IDX]
                ) + (
                    deltas_ciclo[LAST_IDX]
                    if isinstance(deltas_ciclo[LAST_IDX], list)
                    else deltas_ciclo
                )

                omegas_ciclo.pop()
                omegas_ciclo.append(par_candidato)

                vertices_fase = omegas_ciclo

            # Broadcast de las estructuras actualizadas para mantener sincronía entre procesos
            if self.size > 1:
                vertices_fase = self.comm.bcast(vertices_fase, root=0)
                self.memoria_particiones = self.comm.bcast(
                    self.memoria_particiones, root=0
                )

        # Solo el proceso principal determina el resultado final
        if self.rank == 0:
            return min(
                self.memoria_particiones, key=lambda k: self.memoria_particiones[k][0]
            )
        else:
            # Los procesos trabajadores esperan y reciben el resultado final
            return self.comm.bcast(None, root=0)

    def funcion_submodular(
        self, deltas: Union[tuple, list[tuple]], omegas: list[Union[tuple, list[tuple]]]
    ):
        """
        Evalúa el impacto de combinar el conjunto de nodos individual delta y su agrupación con el conjunto omega,
        calculando la diferencia entre EMD (Earth Mover's Distance) de las configuraciones.

        Esta función se ejecuta paralelamente en diferentes procesos, calculando subconjuntos del espacio total de deltas.
        """
        emd_delta = INFTY_NEG
        temporal = [[], []]

        if isinstance(deltas, tuple):
            d_tiempo, d_indice = deltas
            temporal[d_tiempo].append(d_indice)

        else:
            for delta in deltas:
                d_tiempo, d_indice = delta
                temporal[d_tiempo].append(d_indice)

        copia_delta = self.sia_subsistema

        dims_alcance_delta = temporal[EFECTO]
        dims_mecanismo_delta = temporal[ACTUAL]

        particion_delta = copia_delta.bipartir(
            np.array(dims_alcance_delta, dtype=np.int8),
            np.array(dims_mecanismo_delta, dtype=np.int8),
        )
        vector_delta_marginal = particion_delta.distribucion_marginal()
        emd_delta = emd_efecto(vector_delta_marginal, self.sia_dists_marginales)

        # Unión #

        for omega in omegas:
            if isinstance(omega, list):
                for omg in omega:
                    o_tiempo, o_indice = omg
                    temporal[o_tiempo].append(o_indice)
            else:
                o_tiempo, o_indice = omega
                temporal[o_tiempo].append(o_indice)

        copia_union = self.sia_subsistema

        dims_alcance_union = temporal[EFECTO]
        dims_mecanismo_union = temporal[ACTUAL]

        particion_union = copia_union.bipartir(
            np.array(dims_alcance_union, dtype=np.int8),
            np.array(dims_mecanismo_union, dtype=np.int8),
        )
        vector_union_marginal = particion_union.distribucion_marginal()
        emd_union = emd_efecto(vector_union_marginal, self.sia_dists_marginales)

        return emd_union, emd_delta, vector_delta_marginal

    def nodes_complement(self, nodes: list[tuple[int, int]]):
        return list(set(self.vertices) - set(nodes))
