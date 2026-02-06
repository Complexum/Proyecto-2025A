import time
import numpy as np
from src.funcs.iit import ABECEDARY, lil_endian
from src.funcs.format import fmt_biparticion_fuerza_bruta
import math

from pyphi import Network, Subsystem
from pyphi.labels import NodeLabels
from pyphi.models.cuts import Bipartition, Part

from src.middlewares.slogger import SafeLogger
from src.middlewares.profile import gestor_perfilado, profile

from src.models.base.sia import SIA
from src.models.core.solution import Solution
from src.models.enums.temporal_emd import TimeEMD
from src.models.base.application import aplicacion


from src.constants.base import (
    COLS_IDX,
    NET_LABEL,
    TYPE_TAG,
    STR_ONE,
)
from src.constants.models import (
    DUMMY_ARR,
    DUMMY_PARTITION,
    PYPHI_LABEL,
    PYPHI_STRAREGY_TAG,
    PYPHI_ANALYSIS_TAG,
)


class Phi(SIA):
    """Class Phi is used as base for other strategies, bruteforce with pyphi."""

    def __init__(self, tpm: np.ndarray) -> None:
        super().__init__(tpm)
        gestor_perfilado.start_session(
            f"{NET_LABEL}{len(tpm[COLS_IDX])}{aplicacion.pagina_red_muestra}"
        )
        self.logger = SafeLogger(PYPHI_STRAREGY_TAG)

    @profile(context={TYPE_TAG: PYPHI_ANALYSIS_TAG})
    def aplicar_estrategia(
        self,
        estado_inicial: str,
        condiciones: str,
        alcance: str,
        mecanismo: str,
    ):
        self.sia_tiempo_inicio = time.time()
        alcance, mecanismo, subsistema = self.preparar_subsistema(
            estado_inicial, condiciones, alcance, mecanismo
        )
        mip = (
            subsistema.effect_mip(mecanismo, alcance)
            if aplicacion.tiempo_emd == TimeEMD.EMD_EFECTO
            else subsistema.cause_mip(mecanismo, alcance)
        )

        small_phi: float = mip.phi
        repertorio = repertorio_partido = DUMMY_ARR
        format = DUMMY_PARTITION

        if mip.repertoire is not None:
            repertorio = mip.repertoire.flatten()
            repertorio_partido = mip.partitioned_repertoire.flatten()

            states = int(math.log2(mip.repertoire.size))
            sub_estados: np.ndarray = lil_endian(states)

            repertorio.put(sub_estados, repertorio)
            repertorio_partido.put(sub_estados, repertorio_partido)

            mejor_biparticion: Bipartition = mip.partition
            prim: Part = mejor_biparticion.parts[True]
            dual: Part = mejor_biparticion.parts[False]

            prim_mech, prim_purv = prim.mechanism, prim.purview
            dual_mech, dual_purv = dual.mechanism, dual.purview
            format = fmt_biparticion_fuerza_bruta(
                [dual_mech, dual_purv],
                [prim_mech, prim_purv],
            )

        return Solution(
            estrategia=PYPHI_LABEL,
            perdida=small_phi,
            distribucion_subsistema=repertorio,
            distribucion_particion=repertorio_partido,
            tiempo_total=time.time() - self.sia_tiempo_inicio,
            particion=format,
        )

    def preparar_subsistema(
        self, estado_inicio: str, condiciones: str, futuros: str, presentes: str
    ):
        estado_inicial = tuple(int(s) for s in estado_inicio)
        longitud = len(estado_inicial)

        indices = tuple(range(longitud))
        etiquetas = tuple(ABECEDARY[:longitud])

        completo = NodeLabels(etiquetas, indices)
        mpt_estados_nodos_on = self.tpm

        # crear el sistema tras aplicarse las condiciones de fondo puesto si no, entonces se trabajará con uno completo, ya la network sólo se le puede aplicar el subsistema.

        red = Network(tpm=mpt_estados_nodos_on, node_labels=completo)

        candidato = tuple(
            completo[i] for i, bit in enumerate(condiciones) if bit == STR_ONE
        )

        subsistema = Subsystem(network=red, state=estado_inicial, nodes=candidato)
        self.logger.critic("Subsistema creado.")
        alcance = tuple(
            ind
            for ind, (bit, cond) in enumerate(zip(futuros, condiciones))
            if (bit == STR_ONE) and (cond == STR_ONE)
        )
        mecanismo = tuple(
            ind
            for ind, (bit, cond) in enumerate(zip(presentes, condiciones))
            if (bit == STR_ONE) and (cond == STR_ONE)
        )

        return alcance, mecanismo, subsistema
