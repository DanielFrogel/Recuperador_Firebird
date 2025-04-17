import os
import datetime
import zipfile


def file_size(file_path: str) -> str:
    """Retorna string com o tamanho de um arquivo em KB, MB ou GB."""

    try:
        if isinstance(file_path, str):
            size = os.path.getsize(file_path)
        elif isinstance(file_path, int):
            size = file_path

        if size >= 1000000000:
            size_gb = size / (1024 * 1024 * 1024)
            return f"{size_gb:.2f} gb"
        elif size <= 999999:
            size_kb = size / (1024)
            return f"{size_kb:.2f} kb"
        else:
            size_mb = size / (1024 * 1024)
            return f"{size_mb:.2f} mb"
    except:
        return


def zip_file(file_path: str) -> str:
    """Compacta um arquivo em um arquivo zip."""

    try:
        name_zip = os.path.splitext(file_path)[0] + ".zip"
        with zipfile.ZipFile(name_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path, os.path.basename(file_path))

        return name_zip
    except PermissionError as e:
        return e


def backup_name_path(name_path: str, extension: str) -> str:
    """Gera um nome de backup com data e hora para o arquivo do banco de dados."""

    name_temp = name_path.split(".")
    return f"{name_temp[0]}_backup_{(datetime.date.today()).strftime('%d-%m-%Y')}_{(datetime.datetime.now()).strftime('%H-%M')}.{extension}"
