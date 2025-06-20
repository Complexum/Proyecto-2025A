import time
from datetime import datetime

from pathlib import Path
from functools import wraps
from typing import Optional, Callable, Any
from pyinstrument import Profiler
from pyinstrument.renderers import HTMLRenderer
from src.models.base.application import aplicacion


from src.constants.base import (
    PATH_PROFILING,
    HTML_EXTENSION,
)


class ProfilingManager:
    """
    Gestor central de profiling que mantiene configuración y estado
    """

    def __init__(
        self,
        habilitado: bool = aplicacion.profiler_habilitado,
        dir_salida: Path = Path(PATH_PROFILING),
        intervalo: float = 0.001,
    ):
        self.enabled = habilitado
        self.output_dir = dir_salida
        self.interval = intervalo
        self.current_session: Optional[str] = None
        self._setup_directories()

    def _setup_directories(self) -> None:
        """Prepara estructura de directorios para resultados"""
        if self.enabled:
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def start_session(self, session_name: str) -> None:
        if self.enabled:
            # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            timestamp = datetime.now().strftime("%d_%m_%Y/%Hhrs")
            session_path = self.output_dir / session_name / timestamp
            session_path.mkdir(parents=True, exist_ok=True)
            self.current_session = str(session_path.relative_to(self.output_dir))

    def get_output_path(self, name: str, format: str) -> Path:
        """Genera ruta de salida para un perfil específico"""
        session_dir = self.current_session or "default"
        return self.output_dir / session_dir / f"{name}.{format}"


class ProfilerContext:
    """
    Contexto para medición de una función específica
    """

    def __init__(
        self,
        manager: ProfilingManager,
        name: str,
        context: dict,
    ):
        self.manager = manager
        self.name = name
        self.context = context
        self.start_time = None
        self.profiler = (
            None
            if not manager.enabled
            else Profiler(interval=manager.interval, async_mode="disabled")
        )

    def __enter__(self):
        if self.manager.enabled:
            self.start_time = time.perf_counter()
            self.profiler.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.manager.enabled:
            return

        self.profiler.stop()

        # Generar reporte HTML detalladito
        html_path = self.manager.get_output_path(f"{self.name}", HTML_EXTENSION)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(
                self.profiler.output(
                    renderer=HTMLRenderer(show_all=True, timeline=True)
                )
            )


# Instancia global del gestor
gestor_perfilado = ProfilingManager()


def profile(name: Optional[str] = None, context: Optional[dict] = None) -> Callable:
    """
    Decorador para perfilar funciones a nivel de llamados y ejecuciones.

    Args:
        name: Nombre personalizado para el perfil
        context: Información adicional de contexto
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if not gestor_perfilado.enabled:
                return func(*args, **kwargs)

            profile_name = name or func.__name__
            profile_context = {
                **(context or {}),
                "args": str(args),
                "kwargs": str(kwargs),
            }

            with ProfilerContext(
                gestor_perfilado,
                profile_name,
                profile_context,
            ):
                return func(*args, **kwargs)

        return wrapper

    return decorator
