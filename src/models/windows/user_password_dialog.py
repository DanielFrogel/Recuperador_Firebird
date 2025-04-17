import sys
from pathlib import Path
from typing import Tuple
from PyQt6.QtWidgets import (
    QPushButton,
    QLabel,
    QLineEdit,
    QDialog,
    QGridLayout,
)
from PyQt6.QtGui import QIcon


class UserPasswordDialog(QDialog):
    """Classe para criar uma janela de diálogo para inserir o servidor, usuário e senha do banco de dados Firebird."""

    def __init__(self, server_db: str, user_db: str, password_db: str):
        super().__init__()
        self.setWindowTitle("Configurar Firebird")
        self.setFixedSize(300, 150)
        try:
            self.setWindowIcon(
                QIcon(str(Path(sys._MEIPASS) / "src" / "assets" / "icon.ico"))
            )
        except AttributeError:
            self.setWindowIcon(QIcon("src/assets/icon.ico"))

        layout = QGridLayout()

        self.label_user = QLabel("Usuário:")
        self.input_user = QLineEdit(self)
        self.input_user.setText(user_db)
        self.label_password = QLabel("Senha:")
        self.input_password = QLineEdit(self)
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setText(password_db)
        self.label_server = QLabel("IP Server:")
        self.input_server = QLineEdit(self)
        self.input_server.setText(server_db.split("/")[0])
        self.label_port = QLabel("Porta Server:")
        self.input_port = QLineEdit(self)
        self.input_port.setText(server_db.split("/")[1])

        self.button_confirm = QPushButton("Confirmar", self)
        self.button_confirm.clicked.connect(self.confirm)

        layout.addWidget(self.label_user, 0, 0)
        layout.addWidget(self.input_user, 0, 1)
        layout.addWidget(self.label_password, 1, 0)
        layout.addWidget(self.input_password, 1, 1)
        layout.addWidget(self.label_server, 2, 0)
        layout.addWidget(self.input_server, 2, 1)
        layout.addWidget(self.label_port, 3, 0)
        layout.addWidget(self.input_port, 3, 1)
        layout.addWidget(self.button_confirm, 4, 0, 1, 2)

        self.setLayout(layout)

    def confirm(self) -> Tuple[str, str, str]:
        self.accept()

        return (
            self.input_server.text() + "/" + self.input_port.text(),
            self.input_user.text(),
            self.input_password.text(),
        )
