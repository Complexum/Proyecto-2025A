import numpy as np
from numpy.typing import NDArray

from src.models.enums.notation import Notation
from src.constants.error import ERROR_ESPACIOS_INCOMPATIBLES
from src.funcs.iit import reindexar, seleccionar_estado
from src.models.core.ncube import NCube


from src.constants.base import BASE_TWO, COLS_IDX, INT_ZERO
from src.models.base.application import aplicacion


class System:
    """
    La clase sistema es la encargada de realizar las operaciones de condicionamiento, substracción para generación de subsistemas y obtención de las distribuciones marginales para realizar eficientemente el cálculo de la EMD en el Efecto.

    Args:
    ----
        - `tpm` (np.ndarray): El la Matriz de Probabilidad de Transición, de la cuál por cada nodo se generará un n-cubo asociado para permitir rápida operación de los datos.
        - `estado_inicial` (np.ndarray): Este asocia cada variable del sistema con un estado, activa o inactiva, de forma que permita al final seleccionar ciertos estados necesarios para el cálculo final de la EMD.
        - `notation` Optional(str): Por defecto Little-Endian. Representa la notación usada para la indexación de los datos, leer la guía del proyecto para conocer más notaciones.
    """

    def __init__(
        self,
        tpm: np.ndarray,
        estado_inicio: np.ndarray,
    ):
        num_nodos = self.validacion_inicial(tpm, estado_inicio)
        self.estado_inicial = estado_inicio
        self.ncubos = tuple(
            NCube(
                indice=idx,
                dims=np.array(range(num_nodos), dtype=np.int8),
                data=tpm[:, idx].reshape((BASE_TWO,) * num_nodos)
                if aplicacion.indexado_llegada == Notation.LIL_ENDIAN.value
                else tpm[idx, :][reindexar(num_nodos)].reshape((BASE_TWO,) * num_nodos),
            )
            for idx in range(num_nodos)
        )
        self.memo = {}

    def validacion_inicial(self, tpm: np.ndarray, estado_inicio: np.ndarray):
        if estado_inicio.size != (num_nodos := tpm.shape[COLS_IDX]):
            raise ValueError(ERROR_ESPACIOS_INCOMPATIBLES(num_nodos))
        return num_nodos

    @property
    def indices_ncubos(self):
        """
        La TPM tiene asociados una cantidad n-ésima de n-cubos, es por esto que es necesario tenerlos indexados puesto representa el comportamiento de un nodo en todos sus posibles estados dentro de un espacio de probabilidad determinista o estocástica.
        El método ofrece dinámicamente el valor del atributo en función al índice de cada n-cubo.

        Returns:
        -------
            - `np.array`: El listado con los índices con los n-cubos remanentes a la inicialización del sistema, condicionamiento para sistemas candidatos, generación de subsistemas y particiones.
        """
        return np.array([cube.indice for cube in self.ncubos], dtype=np.int8)

    @property
    def dims_ncubos(self):
        """
        Retorna las dimensiones que se preserven en los n-cubos del sistema. No es un método aplicable tras generación de particiones puesto no necesariamente todos los n-cubos mantendrán las mismas dimensiones.

        Returns:
            - `np.ndarray`: El arreglo con las dimensiones únicas de los n-cubos del sistema a cualquier nivel, idealmente superior a una partición.
        """
        return (
            self.ncubos[INT_ZERO].dims if len(self.ncubos) > INT_ZERO else np.array([])
        )

    def condicionar(self, indices: NDArray[np.int8]) -> "System":
        """
        A partir de un sistema origina, esta operación se aplica para todo n-cubo, también llamada como aplicar condiciones de fondo, hace que este se vea seleccionado el cubo en su totalidad, pero delimitando en las dimensiones o indices especificados para hacer selección según el estado inicial asociado.
        Primeramente se intersecan los indices enviados con los actuales de cada n-cubo para evitar elementos inexistentes, luego las dimensiones intersecadas serán las que se definan para cada n-cubo.

        Args:
        ----
            - `indices` (NDArray[np.int8]): Dimensiones que idealmente están asociadas a cada n-cubo y harán selección según el usuario.

        Returns:
        -------
            `System`: El sistema candidato con sus n-cubos condicionados a las variables indicadas y su valor binario específico.
            Este sistema condicionado recibe el nombre de sistema candidato y servirá para procesos de substracción para generación de subsistemas.

        Examples:
        --------
        >>> dimensiones = np.array([2])
        >>> estados = np.array([1,0,0])
        >>> sistema = System(tpm, estados)
        System(indices=[0 1 2], sub_dims=[0 1 2])
            Initial state: [1 0 0]
            NCubes:
                NCube(index=0):
                    dims=[0 1 2]
                    shape=(2, 2, 2)
                    data=
                        [[[0. 0.]
                        [1. 1.]],
                        [[1. 1.]
                        [1. 1.]]]
                NCube(index=1):
                    dims=[0 1 2]
                    shape=(2, 2, 2)
                    data=
                        [[[0. 0.]
                        [0. 0.]],
                        [[0. 1.]
                        [0. 1.]]]
                NCube(index=2):
                    dims=[0 1 2]
                    shape=(2, 2, 2)
                    data=
                        [[[0. 1.]
                        [1. 0.]],
                        [[0. 1.]
                        [1. 0.]]]
        >>> sistema.condicionar(dimensiones)
        System(indices=[0 1], sub_dims=[0 1])
            Initial state: [1 0 0]
            NCubes:
                NCube(index=0):
                    dims=[0 1]
                    shape=(2, 2)
                    data=
                        [[0. 0.]
                        [1. 1.]]
                NCube(index=1):
                    dims=[0 1]
                    shape=(2, 2)
                    data=
                        [[0. 0.]
                        [0. 0.]]

        Como se aprecia se hizo reducción en la dimensión más significativa y prevaleció las dimensiones donde C=0 (agrupamiento más externo, primera posición).
        """
        indices_validos = np.intersect1d(self.indices_ncubos, indices)
        if not indices_validos.size:
            return self
        nuevo_sistema = System.__new__(System)
        nuevo_sistema.estado_inicial = self.estado_inicial
        nuevo_sistema.memo = {}
        nuevo_sistema.ncubos = tuple(
            cube.condicionar(indices_validos, self.estado_inicial)
            for cube in self.ncubos
            if cube.indice not in indices_validos
        )
        return nuevo_sistema

    def substraer(
        self,
        alcance_idx: NDArray[np.int8],
        mecanismo_dims: NDArray[np.int8],
    ) -> "System":
        """
        Permite substraer una serie de elementos a partir de un sistema completo o sun sisteam candidato tanto en el futuro/alcance como el presente/mecanismo, logrando así la generación de un subsistema.

        Args:
        ----
            - `alcance_dims` (NDArray[np.int8]): En este arreglo se encuentran las variables que van a ser eliminadas, puesto es el alcance/futuro significa que los cubos que pertenezcan a estos índices serán descartados.
            - `mecanismo_dims` (NDArray[np.int8]): Acá preceden las dimensiones asociadas a cada n-cubo, donde para cada uno se aplicará la operación de agrupación por promedio, solapando múltiples caras del n-cubo.

        Returns:
        -------
            System: Este subsistema servirá para procesos posteriores de particionamiento.

        Examples:
        --------
        >>> alcances = np.array([0])
        >>> mecanismos = np.array([2])
        >>> mi_sistema
        System(indices=[0 1 2], sub_dims=[0 1 2])
            Initial state: [1 0 0]
            NCubes:
                NCube(index=0):
                    dims=[0 1 2]
                    shape=(2, 2, 2)
                    data=
                        [[[0. 0.]
                        [1. 1.]],
                        [[1. 1.]
                        [1. 1.]]]
                NCube(index=1):
                    dims=[0 1 2]
                    shape=(2, 2, 2)
                    data=
                        [[[0. 0.]
                        [0. 0.]],
                        [[0. 1.]
                        [0. 1.]]]
                NCube(index=2):
                    dims=[0 1 2]
                    shape=(2, 2, 2)
                    data=
                        [[[0. 1.]
                        [1. 0.]],
                        [[0. 1.]
                        [1. 0.]]]
        >>> mi_sistema.substraer(alcances, mecanismos)
        System(indices=[1 2], sub_dims=[0 1])
            Initial state: [1 0 0]
            NCubes:
                NCube(index=1):
                    dims=[0 1]
                    shape=(2, 2)
                    data=
                        [[0.  0.5]
                        [0.  0.5]]
                NCube(index=2):
                    dims=[0 1]
                    shape=(2, 2)
                    data=
                        [[0. 1.]
                        [1. 0.]]

        Los indices asociados a los literales o variables independiente al tiempo son `0:(A|a), 1:(B|b), 2:(C|c)`.
        En el ejemplo se aprecia lo que puede representarse como que el sistema `V={A_abc,B_abc,C_abc}` sufrió una martinalización en `A in (t+1)`, dejando `B` y `C`, sobre los que se aplicó luego una marginalización en `c in (t)`.
        """
        futuros_validos = np.setdiff1d(self.indices_ncubos, alcance_idx)
        nuevo_sistema = System.__new__(System)
        nuevo_sistema.estado_inicial = self.estado_inicial
        nuevo_sistema.memo = {}
        nuevo_sistema.ncubos = tuple(
            cube.marginalizar(mecanismo_dims)
            for cube in self.ncubos
            if cube.indice in futuros_validos
        )
        return nuevo_sistema

    def bipartir(
        self,
        alcance: NDArray[np.int8],
        mecanismo: NDArray[np.int8],
    ) -> "System":
        """
        Es en este método donde generamos a partir de un subsistema, una bipartición.

        Args:
            alcance (NDArray[np.int8]): Variables futuras que idedalmente hacen parte del subsistema, estas seleccionan un subconjunto dentro del mismo el cuál será marginalizado en las dimensiones excluídas.
            mecanismo (NDArray[np.int8]): Acá está el conjunto de dimensiones primales dadas, donde marginalizarán todos los n-cubos cuyo índice no haga parte del alcance.

        Returns:
            System: Se retorna una bipartición, acá es importante tener muy claro que puede o no haber pérdida con respecto al sub-sistema original y por ende, se analizará mediante una distancia métrica cono la EMD-Effect la diferencia entre las distribuciones marginales de estos dos "sistemas", apreciando si hay diferencia como una "pérdida" en la información respecto al sub-sistema original.
        """
        nuevo_sistema = System.__new__(System)
        nuevo_sistema.estado_inicial = self.estado_inicial
        nuevo_sistema.memo = self.memo

        clave = tuple(alcance), tuple(mecanismo)
        if clave not in self.memo:
            self.memo[clave] = tuple(
                cube.marginalizar(np.setdiff1d(cube.dims, mecanismo))
                if cube.indice in alcance
                else cube.marginalizar(mecanismo)
                for cube in self.ncubos
            )
        else:
            print("memo bip")
            self.memo[clave] = self.memo[clave]

        nuevo_sistema.ncubos = self.memo[clave]

        return nuevo_sistema

    def distribucion_marginal(self):
        """
        Partiendo de idealmente un subsistema o una bipartición como entrada, se seleccionana los nodos/elementos cuando su estado es OFF o inactivo para cada uno de ellos, mediante la propiedad de las distribuciones marginales, esto nos permite calcular más eficientemente la EMD-Effect, logrando así determinar un coste para dar comparación entre idealmente, un sub-sistema y una bipartición. Hemos de aplicar una reversión en la selección del estado inicial puesto se está trabajando con el dataset original.

        Returns:
            NDArray[np.float32]: Este arreglo contiene cada elemento/variable de forma ordenada y consecutiva seleccionado específicamente en la clave formada por el estado inicial.
        """
        probabilidad: float
        distribucion = np.empty(self.indices_ncubos.size, dtype=np.float32)

        for i, ncubo in enumerate(self.ncubos):
            probabilidad = ncubo.data
            if ncubo.dims.size:
                inicial = tuple(self.estado_inicial[j] for j in ncubo.dims)
                probabilidad = ncubo.data[seleccionar_estado(inicial)]
            distribucion[i] = probabilidad
        return distribucion

    def __str__(self) -> str:
        sub_dims = self.dims_ncubos
        cubos_info = [f"{c}" for c in self.ncubos]
        return (
            f"\nSystem(indices={self.indices_ncubos}, dims={sub_dims})"
            f"\nInitial state: {self.estado_inicial}"
            f"\nNCubes:\n" + "\n".join(cubos_info)
        )
