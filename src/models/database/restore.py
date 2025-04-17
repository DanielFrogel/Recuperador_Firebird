import os
from typing import Callable
from firebird.driver import (
    connect_server,
    SrvRestoreFlag,
    DatabaseError,
)
from models.utils.file_helper import backup_name_path


def restore(
    path_fbk: str,
    server: str,
    user: str,
    password: str,
    callback_function: Callable[[str], None] = print,
) -> str:
    """Restaurar um banco de dados Firebird a partir de um arquivo de backup (.fbk).

    Args:
        path_fbk (str): Caminho para o arquivo de backup.
        server (str): Endereço do servidor.
        user (str): Nome de usuário para autenticação.
        password (str): Senha para autenticação.
        callback_function (Callable[[str], None]): Função para lidar com mensagens.

    Returns:
        str: Caminho para o arquivo de banco de dados restaurado (.fdb)."""

    try:

        def callback_handler(message: str) -> None:
            if message != "\n":
                return callback_function(message.replace("\n", ""))

        path_temp = path_fbk.split(".")
        path_fdb = path_temp[0] + ".FDB"

        if os.path.exists(path_fdb):
            os.rename(path_fdb, backup_name_path(path_fbk, "FDB"))

        with connect_server(server=server, user=user, password=password) as srv:
            srv.database.restore(
                backup=path_fbk,
                database=path_fdb,
                flags=SrvRestoreFlag.REPLACE,
                stats="TD",
                verbose=True,
                page_size=16384,
                callback=callback_handler,
            )

        return path_fdb

    except DatabaseError as e:
        callback_handler(e)
