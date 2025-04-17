import os
from typing import List, Tuple, Callable
from firebird.driver import (
    connect_server,
    SrvBackupFlag,
    SrvRestoreFlag,
    SrvRepairFlag,
    DatabaseError,
)
from models.utils.file_helper import file_size, backup_name_path


class DataBase:
    """Classe para gerenciar a conexão e operações do banco de dados.
    Fornece métodos para verificar, fazer backup e restaurar o banco de dados.

    Argumentos:
        server (str): O endereço e porta do servidor. O padrão é "localhost/3050".
        user (str): O nome de usuário para a conexão com o banco de dados. O padrão é "SYSDBA".
        password (str): A senha para a conexão com o banco de dados. O padrão é "masterkey".
        db_path (str): O caminho para o arquivo do banco de dados.
    """

    def __init__(
        self,
        server: str = "localhost/3050",
        user: str = "SYSDBA",
        password: str = "masterkey",
        db_path: str = "",
    ) -> None:
        self._server: str = server
        self._user: str = user
        self._password: str = password
        self._db_path: str = ""
        self._db_fbk_path: str = ""

        db_temp: List = db_path.split(".")
        if db_temp[-1].upper() == "FDB":
            self._db_path: str = db_path
            self._db_fbk_path: str = db_temp[0] + ".FBK"
        else:
            self._db_fbk_path: str = db_path
            self._db_path: str = db_temp[0] + ".FDB"

    def set_db_path(self, path: str) -> None:
        db_temp: List = path.split(".")

        if db_temp[-1].upper() == "FDB":
            self._db_path: str = path
            self._db_fbk_path: str = db_temp[0] + ".FBK"
        else:
            self._db_fbk_path: str = path
            self._db_path: str = db_temp[0] + ".FDB"

    def __str__(self) -> str:
        return f"DataBase: {self.db_name}\nPath: {os.path.dirname(self.db_path)}\nSize: {file_size(self.db_path)}"

    @property
    def db_path(self) -> str:
        return str(self._db_path)

    @property
    def fbk_path(self) -> str:
        return str(self._db_fbk_path)

    @property
    def server(self) -> str:
        return str(self._server)

    @property
    def user(self) -> str:
        return str(self._user)

    @property
    def password(self) -> str:
        return str(self._password)

    @property
    def db_name(self) -> str:
        return os.path.basename(self._db_path)

    @property
    def backup_name(self) -> str:
        return backup_name_path(self._db_path, "FDB")

    def config_user(self, server: str, user: str, password: str) -> None:
        """Configura os parâmetros de conexão do banco de dados."""

        self._server = server
        self._user = user
        self._password = password

    def verify_db(self) -> Tuple[bool, str]:
        """Verifica a integridade do banco de dados."""

        try:
            with connect_server(
                server=self.server, user=self.user, password=self.password
            ) as srv:
                srv.database.repair(
                    database=self.db_path,
                    flags=SrvRepairFlag.REPAIR
                    | SrvRepairFlag.IGNORE_CHECKSUM
                    | SrvRepairFlag.MEND_DB
                    | SrvRepairFlag.FULL
                    | SrvRepairFlag.CHECK_DB,
                )
                response: List = srv.readlines()
                if len(response) == 0:
                    return (False, f"Database {self.db_name} Ok")
                else:
                    return (True, "".join(r for r in response))

        except DatabaseError as e:
            return (False, str(e))

    def backup_db(self, callback_function: Callable[[str], None] = print) -> None:
        """Faz o backup do banco de dados para um arquivo .fbk."""

        try:

            def callback_handler(message: str) -> None:
                if (message != "\n") or (message is not None):
                    return callback_function(message.replace("\n", ""))

            with connect_server(
                server=self.server, user=self.user, password=self.password
            ) as srv:
                srv.database.backup(
                    database=self.db_path,
                    backup=self.fbk_path,
                    flags=SrvBackupFlag.IGNORE_CHECKSUMS
                    | SrvBackupFlag.NO_GARBAGE_COLLECT
                    | SrvBackupFlag.IGNORE_LIMBO,
                    stats="TD",
                    verbose=True,
                    callback=callback_handler,
                )
        except DatabaseError as e:
            callback_handler(e)

    def restore_db(self, callback_function: Callable[[str], None] = print) -> None:
        """Restaura o banco de dados a partir de um arquivo .fbk."""

        try:

            def callback_handler(message: str) -> None:
                if message != "\n":
                    return callback_function(message.replace("\n", ""))

            if os.path.exists(self.db_path):
                os.rename(self.db_path, self.backup_name)

            with connect_server(
                server=self.server, user=self.user, password=self.password
            ) as srv:
                srv.database.restore(
                    backup=self.fbk_path,
                    database=self.db_path,
                    flags=SrvRestoreFlag.REPLACE,
                    stats="TD",
                    verbose=True,
                    page_size=16384,
                    callback=callback_handler,
                )

        except DatabaseError as e:
            callback_handler(e)
