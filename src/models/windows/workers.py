from typing import Tuple
from PyQt6.QtCore import QThread, pyqtSignal
from models.database import DataBase, restore
from models.utils.timer import Timer


class RestoreWorker(QThread):
    """Classe para realizar o restore do banco de dados em uma thread separada."""

    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, path_fbk: str, server: str, user_db: str, password_db: str):
        super().__init__()
        self.path_fbk = path_fbk
        self.server: str = server
        self.user_db: str = user_db
        self.user_password: str = password_db

    def run(self):
        try:
            time_execution = Timer()

            self.log_signal.emit("------ Iniciando Restore ------\n")
            restore(
                self.path_fbk,
                self.server,
                self.user_db,
                self.user_password,
                self.log_signal.emit,
            )
        except Exception as e:
            self.log_signal.emit(str(e))
        finally:
            self.log_signal.emit(
                f"\n------ Restore Finalizado em {time_execution} ------"
            )
            self.finished_signal.emit()


class BackupWorker(QThread):
    """Classe para realizar o backup do banco de dados em uma thread separada."""

    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, db: DataBase):
        super().__init__()
        self.db: DataBase = db

    def run(self):
        try:
            time_execution = Timer()

            self.log_signal.emit("------ Iniciando Backup ------\n")
            self.db.backup_db(self.log_signal.emit)
        except Exception as e:
            self.log_signal.emit(str(e))
        finally:
            self.log_signal.emit(
                f"\n------ Backup Finalizado em {time_execution} ------"
            )
            self.finished_signal.emit()


class VerifyWorker(QThread):
    """Classe para realizar a verificação do banco de dados em uma thread separada."""

    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, db: DataBase):
        super().__init__()
        self.db: DataBase = db
        self.db_corrupted: bool = False

    def run(self):
        try:
            time_execution = Timer()

            self.log_signal.emit("------ Iniciando Verificação ------\n")
            self.db_corrupted, response = self.db.verify_db()
            self.log_signal.emit(response)
        except Exception as e:
            self.log_signal.emit(str(e))
        finally:
            self.log_signal.emit(
                f"\n------ Verificação Finalizado em {time_execution} ------"
            )
            self.finished_signal.emit()


class RepairWorker(QThread):
    """Classe para realizar a reparação do banco de dados em uma thread separada."""

    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, db: DataBase):
        super().__init__()
        self.db: DataBase = db

    def run(self):
        try:
            time_execution = Timer()

            self.log_signal.emit("------ Iniciando Reparação ------\n")
            self.log_signal.emit(self.db.verify_db()[1])
            self.db.backup_db(self.log_signal.emit)
            self.db.restore_db(self.log_signal.emit)
            self.log_signal.emit(self.db.verify_db()[1])

        except Exception as e:
            self.log_signal.emit(str(e))
        finally:
            self.log_signal.emit(
                f"\n------ Reparação Finalizado em {time_execution} ------"
            )
            self.finished_signal.emit()
