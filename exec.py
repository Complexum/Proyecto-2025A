from src.models.base.application import aplicacion

from src.main import iniciar
# from src.prueba import iniciar


def main():
    """Inicializar el aplicativo."""

    aplicacion.profiler_habilitado = True
    aplicacion.pagina_sample_network = "B"

    iniciar()


if __name__ == "__main__":
    main()
