from src.middlewares.slogger import SafeLogger
from src.models.base.sia import SIA
from src.funcs.base import ABECEDARY
from itertools import product
from src.funcs.base import emd_efecto
from collections import defaultdict
import time
import numpy as np
from src.models.core.solution import Solution
from src.constants.models import (
    GEOMETRIC_LABEL,
    GEOMETRIC_STRAREGY_TAG,
)

class GeometricSIA(SIA):
    def __init__(self, gestor):
        super().__init__(gestor)
        self.logger = SafeLogger(GEOMETRIC_STRAREGY_TAG)

    def aplicar_estrategia(self, condicion, alcance, mecanismo):
        self.sia_preparar_subsistema(condicion, alcance, mecanismo)
        self.variables = [ABECEDARY[i] for i in self.sia_subsistema.dims_ncubos]
        self.num_vars = len(self.variables)
        self.estado_labels = [''.join(str(b) for b in comb) for comb in product([0,1], repeat=self.num_vars)]
        self.construir_subespacios_geometricos()
        self.tablas_T = {var: defaultdict(dict) for var in self.variables}
        self.memo_costos = {var: {} for var in self.variables}
        self.valores_variables = self._cargar_valores_variables_dinamicos()

        return self.identificar_mejores_biparticiones()

    def construir_subespacios_geometricos(self):
        subespacios = {}
        variables = [ABECEDARY[i] for i in self.sia_subsistema.dims_ncubos]
        num_vars = len(variables)

        for var_idx, var_name in enumerate(variables):
            posiciones_fijas = [i for i in range(num_vars) if i != var_idx]
            subespacio_estados = []

            for fixed_values in product([0, 1], repeat=len(posiciones_fijas)):
                estado_0 = ['0'] * num_vars
                estado_1 = ['0'] * num_vars
                for pos_idx, fixed_pos in enumerate(posiciones_fijas):
                    estado_0[fixed_pos] = str(fixed_values[pos_idx])
                    estado_1[fixed_pos] = str(fixed_values[pos_idx])
                estado_0[var_idx] = '0'
                estado_1[var_idx] = '1'
                subespacio_estados.append(''.join(estado_0))
                subespacio_estados.append(''.join(estado_1))

            subespacios[var_name] = sorted(set(subespacio_estados))
        return subespacios

    def _cargar_valores_variables_dinamicos(self):
        tpm = self.sia_cargar_tpm()
        variable_names = [ABECEDARY[i] for i in self.sia_subsistema.dims_ncubos]
        valores_variables = {var: {} for var in variable_names}

        for row_idx, row in enumerate(tpm):
            estado_bin = format(row_idx, f'0{self.num_vars}b')
            for i, var in enumerate(variable_names):
                valores_variables[var][estado_bin] = row[i]

        return valores_variables

    def encontrar_vecinos_inmediatos(self, i, j):
        vecinos = []
        d_ij = sum(c1 != c2 for c1, c2 in zip(i, j))
        for pos in range(len(i)):
            vecino = list(i)
            vecino[pos] = '1' if i[pos] == '0' else '0'
            vecino_str = ''.join(vecino)
            d_kj = sum(c1 != c2 for c1, c2 in zip(vecino_str, j))
            if d_kj < d_ij:
                vecinos.append(vecino_str)
        return vecinos

    def calcular_costo_bfs_perezoso(self, i, j, var):
        """
        Calcula t(i, j) solo cuando se necesita, 
        con memoización por variable.
        """
        tabla = self.tablas_T[var]
        memo = self.memo_costos[var]
        valores = self.valores_variables[var]

        key = (i, j)
        if key in memo:
            return memo[key]

        d = sum(c1 != c2 for c1, c2 in zip(i, j))
        gamma = 2 ** (-d)
        costo_directo = abs(valores[i] - valores[j])
        if d == 1:
            total = gamma * costo_directo
            tabla[i][j] = total
            memo[key] = total
            return total

        suma_vecinos = 0
        vecinos = self.encontrar_vecinos_inmediatos(i, j)
        for v in vecinos:
            suma_vecinos += self.calcular_costo_bfs_perezoso(v, j, var)

        total = gamma * (costo_directo + suma_vecinos)
        tabla[i][j] = total
        memo[key] = total
        return total

    def identificar_mejores_biparticiones(self):
        emd_scores = []
        variables_presente = [ABECEDARY[i].lower() for i in self.sia_subsistema.dims_ncubos]
        variables_futuro = [ABECEDARY[i] for i in self.sia_subsistema.indices_ncubos]

        print("\n🔍 Comparación de biparticiones (solo marginalizaciones de una variable):")

        for var_pre in variables_presente:
            lado2_presente = [var_pre]
            lado1_presente = [v for v in variables_presente if v != var_pre]
            lado1_futuro = variables_futuro
            lado2_futuro = []

            dims_meca_lado2 = [ABECEDARY.index(var_pre.upper())]
            dims_alca_lado2 = []

            particion = self.sia_subsistema.bipartir(
                np.array(dims_alca_lado2, dtype=np.int8), 
                np.array(dims_meca_lado2, dtype=np.int8))
            dist_marg = particion.distribucion_marginal()
            emd = emd_efecto(dist_marg, self.sia_dists_marginales)

            emd_scores.append((emd, lado2_futuro, lado2_presente, lado1_futuro, lado1_presente, dist_marg))

        for var_fut in variables_futuro:
            lado2_futuro = [var_fut]
            lado1_futuro = [v for v in variables_futuro if v != var_fut]
            lado1_presente = variables_presente
            lado2_presente = []

            dims_alca_lado2 = [ABECEDARY.index(var_fut)]
            dims_meca_lado2 = []

            particion = self.sia_subsistema.bipartir(np.array(dims_alca_lado2, dtype=np.int8), np.array(dims_meca_lado2, dtype=np.int8))
            dist_marg = particion.distribucion_marginal()
            emd = emd_efecto(dist_marg, self.sia_dists_marginales)

            emd_scores.append((emd, lado2_futuro, lado2_presente, lado1_futuro, lado1_presente, dist_marg))

        emd_scores.sort(key=lambda x: x[0])
        perdida_real, l2_fut, l2_pre, l1_fut, l1_pre, dist_marg_opt = emd_scores[0]
        tiempo_total = time.time() - self.sia_tiempo_inicio

        def fmt_biparte_G(lado2_fut, lado1_fut, lado2_pre, lado1_pre):
            def fmt(vs): return ','.join(vs) if vs else '∅'
            return f"⎛ {fmt(lado2_fut)} ⎞⎛ {fmt(lado1_fut)} ⎞\n⎝ {fmt(lado2_pre)} ⎠⎝ {fmt(lado1_pre)} ⎠"

        particion_fmt = fmt_biparte_G(l2_fut, l1_fut, l2_pre, l1_pre)

        return Solution(
            estrategia=GEOMETRIC_LABEL,
            perdida=round(perdida_real, 6),
            distribucion_subsistema=self.sia_dists_marginales,
            distribucion_particion=dist_marg_opt,
            tiempo_total=round(tiempo_total, 4),
            particion=particion_fmt,
        )