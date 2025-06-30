from src.models.base.application import aplicacion
# from tests.pruebas import empezar_pruebitas


from src.main import iniciar


def main():
    """Inicialización del aplicativo"""

    # 👇 Investiga en la clase `aplicación`, para configuraciones 👇 #
    aplicacion.activar_profiling()
    aplicacion.set_pagina_red_muestra("A")

    iniciar()
    # empezar_pruebitas()


if __name__ == "__main__":
    main()
