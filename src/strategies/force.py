from colorama import Fore
from numpy.typing import NDArray
from typing import Callable
import pandas as pd
import numpy as np
import time

from src.models.base.application import aplicacion

from src.models.base.sia import SIA
from src.models.core.system import System
from src.models.core.solution import Solution

from src.middlewares.slogger import SafeLogger
from src.middlewares.profile import profile, gestor_perfilado

from src.funcs.iit import seleccionar_emd, literales
from src.funcs.format import fmt_biparticion
from src.funcs.force import (
    biparticiones,
    generar_candidatos,
    generar_particiones,
    generar_subsistemas,
)
from src.constants.base import (
    COLS_IDX,
    EXCEL_EXTENSION,
    NET_LABEL,
    TYPE_TAG,
    EFFECT,
    ACTUAL,
)
from src.constants.models import (
    BRUTEFORCE_FULL_ANALYSIS_TAG,
    BRUTEFORCE_STRAREGY_TAG,
    BRUTEFORCE_ANALYSIS_TAG,
    BRUTEFORCE_LABEL,
    DUMMY_ARR,
    DUMMY_EMD,
    ERROR_PARTITION,
)


class BruteForce(SIA):
    """
    Generador de soluciones mediante fuerza bruta sobre una red específica.

    Para hacer uso del debug en diferentes zonas del proceso:

    >>>    self.logger.info("General status update")
    >>>    self.logger.debug("Detailed debugging info")
    >>>    self.logger.debuging("debuging message")
    >>>    self.logger.error("Error occurred")

    Así mismo este se almacenará en el archivo con el nombre que hayamos asociado en el `setup_logger(...)`.
    Este archivo de profilling de extensión HTML lo arrastras hasta tu navegador y se visualizará la depuración del aplicativo a lo largo del tiempo en dos vistas, temporal y cumulativa sobre el coste temporal en subrutinas.
    """

    def __init__(self, tpm: np.ndarray):
        super().__init__(tpm)
        gestor_perfilado.start_session(
            f"{NET_LABEL}{tpm[COLS_IDX]}{aplicacion.pagina_red_muestra}"
        )
        self.distancia_metrica: Callable = seleccionar_emd()
        self.logeador = SafeLogger(BRUTEFORCE_STRAREGY_TAG)

    @profile(
        context={TYPE_TAG: BRUTEFORCE_ANALYSIS_TAG}
    )  # Descomentame y revisa el directorio `./review/profiling/`! #
    def aplicar_estrategia(
        self, estado_inicial: str, condiciones: str, alcance: str, mecanismo: str
    ):
        """
        Análisis por fuerza brutal sobre una red específica para un sistema candidato llevado a un subsistema determinado por el alcance y mecanismo indicado por el usuario.

        Args:
        ----
            conditions (str): Condiciones de fondo, dónde se va a condicionar el sistema original como candidato, sean las dimensiones en 0 las que se condicionen.
            alcance (str): Elementos futuros que serán marginalizados si el bit está en cero (0) para la posición de la variable asociada.
            mecanismo (str): Elementos presentes que serán marginalizados si su bit asociado en cero (0) para la posición de la variable.

        Returns:
        -------
            None: El análisis como se aprecia puede ser medido mediante el decorador de profiling, así como si se desea para algún otro método.
        """
        self.sia_preparar_subsistema(estado_inicial, condiciones, alcance, mecanismo)

        solucion_base = Solution(
            BRUTEFORCE_LABEL,
            DUMMY_EMD,
            self.sia_dists_marginales,
            DUMMY_ARR,
            ERROR_PARTITION,
        )

        small_phi = np.inf
        mejor_dist_marg: np.ndarray = DUMMY_ARR

        futuros = self.sia_subsistema.indices_ncubos
        presentes = self.sia_subsistema.dims_ncubos
        biparticion_prim: tuple[tuple[int, ...], tuple[int, ...]]
        biparticion_dual: tuple[tuple[int, ...], tuple[int, ...]]
        m, n = futuros.size, presentes.size

        for subalcance, submecanismo in biparticiones(
            futuros, presentes, (1 << m) * (1 << n)
        ):
            subsistema = self.sia_subsistema
            arr_alcance = np.array(subalcance, dtype=np.int8)
            arr_mecanismo = np.array(submecanismo, dtype=np.int8)

            particion = subsistema.bipartir(arr_alcance, arr_mecanismo)

            part_marg_dist = particion.distribucion_marginal()
            emd_value = self.distancia_metrica(
                part_marg_dist, self.sia_dists_marginales
            )
            if emd_value < small_phi:
                small_phi = emd_value
                mejor_dist_marg = part_marg_dist
                biparticion_prim = submecanismo, subalcance
                biparticion_dual = (
                    set(presentes.data) - set(submecanismo),
                    set(futuros.data) - set(subalcance),
                )

        biparticion_formateada = fmt_biparticion(
            [biparticion_prim[ACTUAL], biparticion_prim[EFFECT]],
            [biparticion_dual[ACTUAL], biparticion_dual[EFFECT]],
        )

        solucion_base.perdida = small_phi
        solucion_base.distribucion_particion = mejor_dist_marg
        solucion_base.particion = biparticion_formateada
        solucion_base.tiempo_ejecucion = time.time() - self.sia_tiempo_inicio
        solucion_base.hablar = True

        return solucion_base

    @profile(context={TYPE_TAG: BRUTEFORCE_FULL_ANALYSIS_TAG})
    def analizar_completamente_una_red(self) -> None:
        """
        Se prepara el directorio de salida donde almacenaremos el análisis completo de una red específica.
        Este análisis consiste de para una red de N elementos en dos tiempos `t_0` y `t_1` para un único estado inicial, se crean todos los `{2^N}-1` factibles sistemas candidatos, posteriormente a cada uno sus `2^{m+n}` posibles biparticiones, excluyendo escenarios con alcances vacíos y finalmente cada bipartición de las `2^{m+n-1}-1` factibles.
        """
        self.tpm.output_dir.mkdir(parents=True, exist_ok=True)

        tpm = self.sia_cargar_tpm()
        initial_state = np.array(
            [canal for canal in self.tpm.estado_inicial],
            dtype=np.int8,
        )
        # system = System(tpm, initial_state, debug_observer)
        system = System(tpm, initial_state)
        self.__analizar_candidatos(system)
        print(f"""
{Fore.RED}Generación finalizada!{Fore.BLUE}\nRevisa tu directorio `review/resolver/`.
{Fore.WHITE}Tamaño de la red: {initial_state.size} nodos.
Estado incial: {initial_state}.
""")

    def __analizar_candidatos(self, sistema: System) -> None:
        """
        Genera todos los sistemas candidatos factibles para dar análisis, de forma que se almacenen luego como un documento excel para mejor visualización.

        Args:
        ----
            sistema (System): Sisteam completo que será condicionado según la combinación de dimensiones para condicionar/eliminar, formando el sistema candidato.
        """
        cantidad = len(self.tpm.estado_inicial)
        dim_candidatas = generar_candidatos(cantidad)

        for dimensiones in dim_candidatas:
            self.__procesar_candidato(sistema, np.array(dimensiones, dtype=np.int8))

    def __procesar_candidato(
        self, completo: System, condiciones: NDArray[np.int8]
    ) -> None:
        """Aplicamos condiciones de fondo sobre el sistema completo y continuamos la cadena para su análisis por subsistemas.

        Args:
        ----
            completo (System): Sistema completo a condicionar.
            condiciones (NDArray[np.int8]): Condiciones de fondo aplicadas sobre el sistema completo.
        """
        candidato = completo.condicionar(condiciones)
        nombre = literales(np.setdiff1d(candidato.dims_ncubos, condiciones))
        self.__procesar_subsistema(candidato, nombre)

    def __procesar_subsistema(
        self, mecanismo_removido: System, nombre_candidato: str
    ) -> None:
        """
        Genera todos los subsistemas para un sistema candidato.

        Args:
        ----
            mecanismo_removido (System): Mecanismo obtenido de algún condicionamiento realizado con anterioridad.
            nombre_candidato (str): El noombre del sistema candidato de forma amigable, este determinará el nombre del fichero donde se guardará la solución de su análisis, esto en el directorio `review/`.
        """
        results_file = self.tpm.output_dir / f"{nombre_candidato}.{EXCEL_EXTENSION}"

        with pd.ExcelWriter(results_file) as writer:
            for alcance_removido, sub_present in generar_subsistemas(
                mecanismo_removido.dims_ncubos
            ):
                if not self.__deberia_omitir_subsistema(
                    alcance_removido, mecanismo_removido
                ):
                    self.__analizar_subsistema(
                        mecanismo_removido,
                        np.array(alcance_removido, dtype=np.int8),
                        np.array(sub_present, dtype=np.int8),
                        writer,
                    )

    def __deberia_omitir_subsistema(
        self, alcance_removido: tuple[int, ...], candidate: System
    ) -> bool:
        """
        Revisa si el alcance o futuro que se va a condicionar genera un subsistema sin futuro y por ende, no útil en el análisis sistémico, no hay un non-trivial effect cual dar revisión.

        Args:
        ----
            alcance_removido (tuple[int, ...]): tupla con índices asociados a las dimensiones que serán removidas.
            candidate (System): Sistema cual se removeran los alcances.

        Returns:
        -------
            bool: Determina si tienen el mismo tamaño, de serlo su diferencia será 0 y por ende no habrá futuro.
        """
        return len(alcance_removido) == candidate.indices_ncubos.size

    def __analizar_subsistema(
        self,
        candidato: System,
        alcance_removido: NDArray[np.int8],
        mecanismo_removido: NDArray[np.int8],
        writer: pd.ExcelWriter,
    ) -> None:
        """Analiza un sistema candidato y genera un condicionamiento para analizar sus subsistemas restantes.

        Args:
        ----
            candidato (System): Subsistema candidato a ser substraído de sus elementos con el fin de obtener un subsistema.
            alcance_removido (NDArray[np.int8]): El alcance o elementos futuros que serán marginalizados.
            mecanismo_removido (NDArray[np.int8]): El mecanismo o elementos presentes que serán marginalizados.
            writer (pd.ExcelWriter): escritor en la hoja de cálculo para un documento excel ya asociado.

        Se almacena el resultado del análisis de este subsistema en una hoja de excel con la representación literal del mismo.
        """
        subsistema = candidato.substraer(alcance_removido, mecanismo_removido)
        dist_marginal = subsistema.distribucion_marginal()

        nombre_subsistema = self.__get_nombre_subsistema(
            candidato, alcance_removido, mecanismo_removido
        )
        resultado = self.__analizar_particiones(dist_marginal, subsistema)
        resultado.to_excel(writer, sheet_name=nombre_subsistema)

    def __analizar_particiones(
        self, distribucion: NDArray[np.float32], subsistema: System
    ) -> pd.DataFrame:
        """Para cada subsistema se realiza su análisis por cada partición. Como tenemos entendido la primera partición es tirivial de forma que es ignorada (esto es representado luego con i=1 para la selección de etiquetas).
        Primeramente se obtienen las dimensiones totales del subsistema, tanto para mecanismos/filas (n) como alcances/columnas (m), sabemos que la cantidad de particiones con `k=2` (biparticiones) `P_k(S_{n, m}) = 2^(m+n-1)-1 = [(2^m-1)*(2^{n})]-1`, con esto podemos generar una matriz de `2^m` filas por `2^(m-1)` columnas y sustraemos la partición trivial.
        Precomputamos las llaves y así mismo las posibles particiones, donde indexamos el resultado de la emd claramente en el iterando módulo m o n para asociar correctamente la clave e incrementamos ambos, pero sólo j cuando i haga una rotación.
        Como se aprecia en el fichero `resolver/<red específica>/<estado inicial>/` la partición que interseca las claves (0,0) siempre debe estar vacía puesto es la partición trivial (donde de hecho no es una partición pues toda variable pertenece al mismo lado).

        Args:
        ----
            distribucion (NDArray[np.float32]): Distribución marginal que se comparará con la distribución marginal de la partición
            subsistema (System): Subsistema que será particionado y su partición analizada con este mismo mediante la EMD Efecto

        Returns:
        -------
            pd.DataFrame: Matriz que asociará en las filas los elementos presente o mecanismos de la partición y en las columnas los elementos futuros o alcances de la partición, esto de forma que los elementos que pertenezcan al mismo bit (0|1), pertenecen a la misma partición.
        """
        m, n = subsistema.indices_ncubos.size, subsistema.dims_ncubos.size

        llave_presente = [f"{number:0{n}b}" for number in range(1 << n)]
        llave_futuro = [f"{number:0{m}b}" for number in range(1 << m - 1)]

        resultados = pd.DataFrame(
            columns=llave_futuro,
            index=llave_presente,
            dtype=np.float32,
        )

        i, j = 1, 0
        for alcance, mecanismo in generar_particiones(m, n):
            sub_alcance = np.array([i for i, bit in enumerate(alcance) if bit])
            sub_mecanismo = np.array([i for i, bit in enumerate(mecanismo) if bit])

            particion = subsistema.bipartir(
                np.array(sub_alcance, dtype=np.int8),
                np.array(sub_mecanismo, dtype=np.int8),
            )

            dist_parte_marginal = particion.distribucion_marginal()
            emd_value = self.distancia_metrica(dist_parte_marginal, distribucion)

            etiqueta_mecanismo = "".join(map(str, mecanismo.astype(int)))
            etiqueta_alcance = "".join(map(str, alcance.astype(int)))

            # Asignar el valor al DataFrame
            resultados.loc[etiqueta_mecanismo, etiqueta_alcance] = emd_value

        return resultados

    def __get_nombre_subsistema(
        self,
        candidato: System,
        sub_alcance: NDArray[np.int8],
        sub_mecanismo: NDArray[np.int8],
    ) -> str:
        """
        Muestra de forma amigable el subsistema analizado, utilizando literales asociados con la dimensión respectiva.

        Args:
            candidato (System): Sistema candidato del que se obtendrán las dimensiones a ser representadas de tanto el mecanismo presente, como el alcance futuro.
            sub_alcance (NDArray[np.int8]): Alcance que será eliminado en el proceso.
            sub_mecanismo (NDArray[np.int8]): Mecanismo que será eliminado en el proceso.

        Returns:
            str: Literal con la representación del subsistema
        """
        futuro_removido = np.setdiff1d(candidato.dims_ncubos, sub_alcance)
        presente_removido = np.setdiff1d(candidato.dims_ncubos, sub_mecanismo)
        return f"{literales(futuro_removido)}|{literales(presente_removido)}"
