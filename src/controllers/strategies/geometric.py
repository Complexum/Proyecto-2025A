import numpy as np
import time
import itertools
from src.models.base.sia import SIA
from src.models.core.solution import Solution
from src.funcs.base import emd_efecto

class GeometricSIA(SIA):
    def __init__(self, gestor_sistema, **kwargs):
        super().__init__(gestor_sistema, **kwargs)
        self.memo_costos = {}
        self.memo_distribuciones = {}

    def aplicar_estrategia(self, condicion, alcance, mecanismo):
        """
        Punto de entrada estándar para el framework.
        """
        self.sia_tiempo_inicio = time.time()
        self.sia_preparar_subsistema(condicion, alcance, mecanismo)
        n_vars = len(self.sia_subsistema.estado_inicial)

        # 3: tensors ← DescomponerEnTensores(S)
        tpm = getattr(self.sia_subsistema, 'tpm', None)
        if tpm is None and hasattr(self.sia_subsistema, 'get_tpm'):
            tpm = self.sia_subsistema.get_tpm()
        elif tpm is None:
            tpm = self.sia_cargar_tpm()
        self.tpm_subsistema = tpm

        tensores = self.descomponer_en_tensores(tpm, n_vars)

        # 4: T ←InicializarTablaDeTransiciones()
        # size = 2 ** n_vars
        # T = np.zeros((n_vars, size, size), dtype=np.float32)
        self.memo_costos = {}

        # Ya no recorremos todos los i, j y v para llenar T.
        # Los costos de transición se calcularán bajo demanda en calcular_costo_transicion.

        # 12: candidates ← IdentificarBiparticionesCandidatas(T)
        candidates = self.identificar_biparticiones_candidatas(n_vars)

        # 13: Bopt ← EvaluarCandidatos(candidates, S, T)
        mejor = self.evaluar_candidatos(candidates)

        tiempo_total = time.time() - self.sia_tiempo_inicio
        self.sia_logger.info(f"[GeometricSIA] Tiempo ejecución: {tiempo_total:.3f} s")

        # 14: return Bopt (formato Solution)
        return Solution(
            estrategia="Geometric",
            perdida=mejor["costo"],
            distribucion_subsistema=self.sia_dists_marginales,
            distribucion_particion=mejor["distribucion"],
            particion=mejor["particion"],
        )
    def descomponer_en_tensores(self, tpm, n_vars):
        """
        Descompone el sistema en tensores para cada variable.
        """
        size = tpm.shape[0]
        tensores = []
        for v in range(n_vars):
            tensor_v = np.zeros((size, 2), dtype=np.float32)
            for i in range(size):
                p = tpm[i, v]
                tensor_v[i, 1] = p
                tensor_v[i, 0] = 1 - p
            tensores.append(tensor_v)
        return tensores

    def calcular_costo_transicion(self, i, j, v, tensor_v):
        key = (i, j, v)
        if key in self.memo_costos:
            return self.memo_costos[key]

        n_vars = int(np.log2(tensor_v.shape[0]))
        d = bin(i ^ j).count('1')
        gamma = 2 ** (-d) if d > 0 else 1.0

        valor_en_j = (j >> (n_vars - 1 - v)) & 1
        prob_cond = tensor_v[i, valor_en_j]
        diferencia = abs(prob_cond - 1.0)  # Diferencia entre prob condicional y valor real

        if d <= 1:
            resultado = gamma * diferencia
            self.memo_costos[key] = resultado
            return resultado

        vecinos = []
        for bit in range(n_vars):
            vecino = i ^ (1 << (n_vars - 1 - bit))
            d_vecino = bin(vecino ^ j).count('1')
            if d_vecino == d - 1:
                vecinos.append(vecino)

        suma_vecinos = sum(self.calcular_costo_transicion(k, j, v, tensor_v) for k in vecinos)
        resultado = gamma * (diferencia + suma_vecinos)
        self.memo_costos[key] = resultado
        return resultado
    
    def identificar_biparticiones_candidatas(self, n_vars):
        """
        Genera biparticiones candidatas como pares de conjuntos de índices.
        Ahora genera todas las particiones no triviales (no vacías ni todo el conjunto).
        """
        indices = set(range(n_vars))
        candidates = []
        # Para evitar duplicados, solo tomamos subconjuntos de tamaño 1 a n_vars//2
        for r in range(1, n_vars // 2 + 1):
            for subset in itertools.combinations(indices, r):
                conjunto1 = set(subset)
                conjunto2 = indices - conjunto1
                candidates.append((conjunto1, conjunto2))
        return candidates

    def evaluar_candidatos(self, candidates):
        """
        Evalúa cada bipartición candidata y retorna la mejor.
        """
        mejor_costo = float('inf')
        mejor_particion = None
        mejor_distribucion = None

        for conj1, conj2 in candidates:
            key = tuple(sorted(conj1))
            if key in self.memo_distribuciones:
                dist_marginal = self.memo_distribuciones[key]
            else:
                try:
                    dist_marginal = self.sia_subsistema.distribucion_marginal(np.array(list(conj1), dtype=np.int8))
                except Exception:
                    dist_marginal = self.sia_dists_marginales
                self.memo_distribuciones[key] = dist_marginal

            perdida = emd_efecto(dist_marginal, self.sia_dists_marginales)

            if perdida < mejor_costo:
                mejor_costo = perdida
                mejor_particion = (conj1, conj2)
                mejor_distribucion = dist_marginal

        return {
            "costo": mejor_costo,
            "particion": mejor_particion,
            "distribucion": mejor_distribucion,
        }