from enum import Enum


class TimeEMD(Enum):
    """La clase temporal emd recopila diferentes tipos de emd según su tiempo. Al definir el enum se accede por `.value`."""

    EMD_EFECTO = "emd-effect"
    EMD_CAUSA = "emd-cause"
    EMD_INTEGRADA = "emd-cause-effect"
