from src.models.base.application import aplicacion

from src.main import iniciar


def main():
    """Inicialización del aplicativo"""

    aplicacion.activar_profiling()
    aplicacion.set_pagina_red_muestra("A")

    iniciar()


if __name__ == "__main__":
    main()
