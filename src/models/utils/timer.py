from time import perf_counter


class Timer:
    """Classe simples para medir o tempo decorrido."""

    def __init__(self) -> None:
        self.start_time: float = perf_counter()

    def __str__(self) -> str:
        end_time: float = perf_counter()
        elapsed_time: float = end_time - self.start_time

        if elapsed_time > 60 and elapsed_time < 3600:
            minutes: int = int(elapsed_time // 60)
            seconds: float = elapsed_time % 60
            return f"{minutes}m {seconds:.2f}s"
        elif elapsed_time > 3600:
            hours: int = int(elapsed_time // 3600)
            minutes: int = int((elapsed_time % 3600) // 60)
            seconds: float = elapsed_time % 60
            return f"{hours}h {minutes}m {seconds:.2f}s"
        else:
            return f"{elapsed_time:.2f}"
