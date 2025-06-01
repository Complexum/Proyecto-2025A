from src.models.base.application import aplicacion
# from src.alt import iniciar
# from src.prueba import iniciar

from src.main import iniciar


def main():
    """Inicializar el aplicativo."""

    aplicacion.profiler_habilitado = True
    aplicacion.pagina_sample_network = "A"

    iniciar()


if __name__ == "__main__":
    main()
