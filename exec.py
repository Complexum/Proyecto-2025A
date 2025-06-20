from src.models.enums.temporal_emd import TemporalEMD
from src.models.base.application import aplicacion

from src.main import iniciar


def main():
    """Inicializar el aplicativo."""

    aplicacion.activar_profiling()
    aplicacion.set_pagina_red_muestra("A")
    aplicacion.set_tiempo_emd(TemporalEMD.EMD_CAUSA.value)

    iniciar()


if __name__ == "__main__":
    main()
