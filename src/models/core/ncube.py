from dataclasses import dataclass, field
from numpy.typing import NDArray
import numpy as np


@dataclass(frozen=True)
class NCube:
    """
    N-cubo hace referencia a un cubo n-dimensional, donde estarán indexados según la posición de precedencia de los datos, permitiendo el rápido acceso y operación en memoria.
    - `indice`: índice original del n-cubo asociado con un literal (0:A, 1:B, 2:C, ...) que permita representabilidad en su alcance o tiempo futuro.
    - `dims`: dimensiones activas actuales del n-cubo, es aquí donde se conoce la dimensionalidad según su cantidad de elementos, de forma tal que si este en el tiempo es condicionado o marginalizado tendrá una dimensionalidad menor o igual a la original a pesar que haya una alta dimensión específica.
    - `data`: arreglo numpy con los datos indexados según la notación de origen, de ser necesario se aplica una transformación sobre estos que los reindexe si se desea otra notación particular.
    """

    indice: int
    dims: NDArray[np.int8]
    data: np.ndarray
    memo: dict[tuple[tuple[int, int], ...], np.ndarray] = field(default_factory=dict)

    def __post_init__(self):
        """Validación de tamaño y dimensionalidad tras inicialización.

        Raises:
            ValueError: Se valida que hayan dimensiones y cumpla con las dimensiones de un cubo n-dimensional.
        """
        if self.dims.size and self.data.shape != (2,) * self.dims.size:
            raise ValueError(
                f"Forma inválida {self.data.shape} para dimensiones {self.dims}"
            )

    def condicionar(
        self,
        indices_condicionados: NDArray[np.int8],
        estado_inicial: NDArray[np.int8],
    ) -> "NCube":
        """
        Aplicar condiciones de fondo sobre un n-cubo. En estas lo que se hace es seleccionar una serie de caras sobre el n-cubo según las dimensiones escogidas y su estado inicial específico asociado, descartandose así todas las demás que no pertenezcan al indice condicionado.
        En la selección de las dimensiones es importante saber cómo la dimensión más externa es la más significativa, de forma que la selección debe hacerse de afuera hacia adentro.
        Debe tenerse claro también la localidad de las dimensiones puesto aunque se tengan dimensiones muy superiores no hay correspondencia con el total de dimensiones del cubo (dimensiones locales).

        Args:
        ----------
            indices_condicionados (NDArray[np.int8]): Dimensiones o ejes en los cuales se aplicará el condicinamiento.
            estado_inicial (NDArray[np.int8]): El estado inicial asociado al sistema.

        Returns:
        -------

            NCube: El n-cubo seleccionado en todos los ejes, pero se definen para dar selección los cuales se hayan enviado como parámetros.

        Example:
        -------
        El n-cubo original está asociado con el estado inicial

        >>> estado_inicial = np.array([1,0,0])
        >>> mi_ncubo
            NCube(index=(1,)):
                dims=(0, 1, 2)
                shape=(2, 2, 2)
                data=
                    [[[0.1  0.3 ]
                    [0.5  0.7 ]]
                    [[0.9  0.11]
                    [0.13 0.15]]]
        >>> dimensiones = np.array([2])
        >>> mi_ncubo.condicionar(dimensiones, estado_incial)
            NCube(index=(1,)):
                dims=(0, 1)
                shape=(2, 2)
                data=
                    [[0.1 0.3]
                    [0.5 0.7]]
        """

        numero_dims = self.dims.size
        seleccion = [slice(None)] * numero_dims

        for condicion in indices_condicionados:
            level_arr = numero_dims - (condicion + 1)
            seleccion[level_arr] = estado_inicial[condicion]

        nuevas_dims = np.array(
            [dim for dim in self.dims if dim not in indices_condicionados],
            dtype=np.int8,
        )
        return NCube(
            data=self.data[tuple(seleccion)],
            indice=self.indice,
            dims=nuevas_dims,
        )

    def marginalizar(self, ejes: NDArray[np.int8]) -> "NCube":
        """
        Marginalizar a nivel del n-cubo permite acoplar o colapsar una o más dimensiones manteniendo la probabilidad condicional.
        El n-cubo puede esquematizarse de forma tal que se aprecia un solapamiento/promedio ente sus dimensiones, donde la dimensión más baja es el primer desplazamiento dimensional sobre el arreglo.
        Es importante validar la intersección de ejes puesto es una rutina llamada en sistema desde marginalizar como particionar.

        Args:
        ----
            ejes (NDArray[np.int8]): Arreglo con las dimensiones a marginalizar o eliminar. Se valida que los ejes o dimensiones dadas estén y finalmente alineamos nuevamente con las dimensiones locales, con numpy debemos hacer uso de la dimensión complementaria para alinear desde la dimensión externa hasta la interna.

        Returns:
        -------
            NCube: El n-cubo marginalizado en las dimensiones dadas. Es equivalente marginalizar sobre (a, b,) sea primero en (a,) y luego en (b,) o viceversa.

        Example:
        -------
            >>> dimensiones = np.array([1, 2])
            >>> mi_ncubo
            NCube(index=0):
            dims=[0 1 2]
            shape=(2, 2, 2)
            data=
                [[[0. 0.]
                  [1. 1.]],
                 [[1. 1.]
                  [1. 1.]]]

            >>> mi_ncubo.marginalizar(dimensiones)
            NCube(index=0):
                dims=[0]
                shape=(2,)
                data=
                    [0.75 0.75]

            Se han agrupado los valores del n-cubo por promedio, dejando los remanentes en la dimension 0.
        """
        if tuple(ejes) not in self.memo:
            marginable_axis = np.intersect1d(ejes, self.dims)
            if not marginable_axis.size:
                return self
            numero_dims = self.dims.size - 1
            ejes_locales = tuple(
                numero_dims - dim_idx
                for dim_idx, axis in enumerate(self.dims)
                if axis in marginable_axis
            )
            new_dims = np.array(
                [d for d in self.dims if d not in marginable_axis],
                dtype=np.int8,
            )
            self.memo[tuple(ejes)] = (
                np.mean(self.data, axis=ejes_locales, keepdims=False),
                new_dims,
            )
        return NCube(
            data=self.memo[tuple(ejes)][0],
            dims=self.memo[tuple(ejes)][1],
            indice=self.indice,
        )

    def __str__(self) -> str:
        dims_str = f"dims={self.dims}"
        forma_str = f"shape={self.data.shape}"
        datos_str = str(self.data).replace("\n", "\n" + " " * 8)
        return (
            f"NCube(index={self.indice}):\n"
            f"    {dims_str}\n"
            f"    {forma_str}\n"
            f"    data=\n        {datos_str}"
        )
