import sys
import logging
from pathlib import Path
from datetime import datetime
from functools import wraps
from typing import Any, Callable

from colorama import init, Fore, Style

from src.constants.base import PATH_LOGS


class ColorFormatter(logging.Formatter):
    """Formatter personalizado para consola con colores usando colorama."""

    COLORS = {
        logging.DEBUG: Fore.LIGHTBLACK_EX,  # gris
        logging.INFO: Fore.BLUE,  # azul
        logging.WARNING: Fore.YELLOW,  # amarillo
        logging.ERROR: Fore.RED,  # rojo
        logging.CRITICAL: Fore.MAGENTA,  # magenta
        logging.FATAL: Fore.RED + Style.BRIGHT,  # rojo brillante
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        init(autoreset=True)  # Inicializa colorama

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, "")
        # Guarda el nombre del nivel original
        original_levelname = record.levelname
        # Aplica el color al nombre del nivel
        record.levelname = f"{color}{original_levelname}{Style.RESET_ALL}"

        # Formato del mensaje
        formatted = super().format(record)
        # Restaura el nombre del nivel original
        record.levelname = original_levelname
        return formatted


class SafeLogger:
    """Logger seguro/robusto para manejar cualquier tipo de entrada y caracteres especiales."""

    def __init__(self, name: str):
        self._logger = self.__setup_logger(name)

    def _safe_str(self, obj: Any) -> str:
        """Convierte cualquier objeto a string de forma segura."""
        try:
            if isinstance(obj, (list, tuple, set, dict)):
                return str(obj)
            return str(obj).encode("utf-8", errors="replace").decode("utf-8")
        except Exception:
            return "[Objeto no representable]"

    def _safe_format(self, *args, **kwargs) -> str:
        """Formatea los argumentos de forma segura."""
        args_str = " ".join(self._safe_str(arg) for arg in args)
        if kwargs:
            kwargs_str = " ".join(f"{k}={self._safe_str(v)}" for k, v in kwargs.items())
            return f"{args_str} {kwargs_str}"
        return args_str

    def __setup_logger(self, name: str) -> logging.Logger:
        """Configura el logger con manejo de encodings y formateo personalizado."""
        # Crear estructura de directorios para logs detallados
        base_log_dir = Path(PATH_LOGS)
        base_log_dir.mkdir(exist_ok=True)

        current_time = datetime.now()
        date_dir = base_log_dir / current_time.strftime("%d_%m_%Y")
        date_dir.mkdir(exist_ok=True)

        hour_dir = date_dir / f"{current_time.strftime('%H')}hrs"
        hour_dir.mkdir(exist_ok=True)

        # Archivo para logs detallados
        detailed_log_file = hour_dir / f"{name}.log"
        # Archivo para el último log
        last_log_file = base_log_dir / f"last_{name}.log"

        logger = logging.getLogger(name)
        logger.setLevel(logging.ERROR)
        # Importante: evita la propagación a loggers padre
        logger.propagate = False
        logger.handlers.clear()

        # Formatter para archivos (sin colores)
        plain_formatter = logging.Formatter(
            "%(asctime)s [%(name)s] %(levelname)s %(processName)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",  # Removido %f para evitar el error
        )

        # Formatter para consola (con colores)
        colored_formatter = ColorFormatter(
            "%(levelname)s (%(asctime)s): %(message)s",
            datefmt="%H:%M:%S",  # Formato simplificado para la consola
        )

        # Handler para archivo detallado
        detailed_file_handler = logging.FileHandler(
            detailed_log_file, mode="w", encoding="utf-8"
        )
        detailed_file_handler.setLevel(logging.DEBUG)
        detailed_file_handler.setFormatter(plain_formatter)

        # Handler para el archivo "last"
        last_file_handler = logging.FileHandler(
            last_log_file, mode="w", encoding="utf-8"
        )
        last_file_handler.setLevel(logging.DEBUG)
        last_file_handler.setFormatter(plain_formatter)

        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(
            logging.DEBUG
        )  # Cambiado a DEBUG para ver todos los mensajes
        console_handler.setFormatter(colored_formatter)

        logger.addHandler(detailed_file_handler)
        logger.addHandler(last_file_handler)
        logger.addHandler(console_handler)

        return logger

    def set_log(self, level: int, *args, **kwargs) -> None:
        """Método genérico de logging."""
        message = self._safe_format(*args, **kwargs)
        self._logger.log(level, message)

    def debug(self, *args, **kwargs) -> None:
        """Log a nivel DEBUG."""
        self.set_log(logging.DEBUG, *args, **kwargs)

    def info(self, *args, **kwargs) -> None:
        """Log a nivel INFO."""
        self.set_log(logging.INFO, *args, **kwargs)

    def warn(self, *args, **kwargs) -> None:
        """Log a nivel WARNING."""
        self.set_log(logging.WARNING, *args, **kwargs)

    def error(self, *args, **kwargs) -> None:
        """Log a nivel ERROR."""
        self.set_log(logging.ERROR, *args, **kwargs)

    def critic(self, *args, **kwargs) -> None:
        """Log a nivel CRITICAL."""
        self.set_log(logging.CRITICAL, *args, **kwargs)

    def fatal(self, *args, **kwargs) -> None:
        """Log a nivel FATAL."""
        self.set_log(logging.FATAL, *args, **kwargs)


def get_logger(name: str) -> SafeLogger:
    """Función de conveniencia para obtener una instancia del logger."""
    return SafeLogger(name)


# Decorador opcional para logging automático
def log_execution(logger: SafeLogger):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.debug(f"Iniciando {func.__name__}")
                result = func(*args, **kwargs)
                logger.debug(f"Completado {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Error en {func.__name__}: {e}")
                raise

        return wrapper

    return decorator
