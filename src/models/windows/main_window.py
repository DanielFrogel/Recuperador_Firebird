import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QFileDialog,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMenuBar,
    QLabel,
    QPlainTextEdit,
    QStatusBar,
)
from PyQt6.QtGui import QIcon

from models.windows.user_password_dialog import UserPasswordDialog
from models.windows.workers import (
    BackupWorker,
    VerifyWorker,
    RestoreWorker,
    RepairWorker,
)
from models.database import DataBase
from models.utils.file_helper import file_size, zip_file


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recuperador Firebird")
        self.setFixedSize(600, 400)
        try:
            self.setWindowIcon(
                QIcon(str(Path(sys._MEIPASS) / "src" / "assets" / "icon.ico"))
            )
        except AttributeError:
            self.setWindowIcon(QIcon("src/assets/icon.ico"))

        self.user_db: str = "SYSDBA"
        self.password_db: str = "masterkey"
        self.server_db: str = "localhost/3050"
        self.db: DataBase = None

        self.button_select = QPushButton("Selecionar Banco de Dados", self)
        self.button_select.setToolTip(
            "Necessário selecionar o .FBD para realizar as funções de Verificação/Backup e Otimização"
        )

        self.button_verify = QPushButton("Verificar", self)
        self.button_verify.setToolTip("Verifica se o banco de dados está corrompido")

        self.button_repair = QPushButton("Reparar/Otimizar", self)
        self.button_repair.setToolTip(
            "Backup e Recuperação do banco de dados corrompido ou para otimização"
        )

        self.button_backup = QPushButton("Backup", self)
        self.button_backup.setToolTip("Backup do banco de dados e opção de compactar")

        self.button_restore = QPushButton("Restaurar", self)
        self.button_restore.setToolTip("Restauração de arquivo .fbk para .fdb")

        self.button_select.clicked.connect(lambda: self.select_db())
        self.button_verify.clicked.connect(self.verify_db)
        self.button_repair.clicked.connect(self.repair_db)
        self.button_backup.clicked.connect(self.backup_db)
        self.button_restore.clicked.connect(self.select_restore)

        layout_button = QHBoxLayout()
        layout_button.addWidget(self.button_select)
        layout_button.addWidget(self.button_verify)
        layout_button.addWidget(self.button_repair)
        layout_button.addWidget(self.button_backup)
        layout_button.addWidget(self.button_restore)

        self.console = QPlainTextEdit(self)
        self.console.setReadOnly(True)

        layout_principal = QVBoxLayout()
        layout_principal.addLayout(layout_button)
        layout_principal.addWidget(self.console)

        central_widget = QWidget()
        central_widget.setLayout(layout_principal)
        self.setCentralWidget(central_widget)

        menu_bar = QMenuBar(self)
        menu_bar.addAction("Configurar Firebird", self.open_dialog_user_password)
        self.setMenuBar(menu_bar)

        self.list_menus: list[QWidget] = [
            self.button_select,
            self.button_verify,
            self.button_repair,
            self.button_backup,
            self.button_restore,
            menu_bar,
        ]

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.label_left = QLabel("")
        self.label_right = QLabel("")

        self.status_bar.addWidget(self.label_left, 3)
        self.status_bar.addPermanentWidget(self.label_right, 1)

        self.disable_menus(True)

    def disable_menus(self, disable: bool) -> None:
        self.button_verify.setDisabled(disable)
        self.button_repair.setDisabled(disable)
        self.button_backup.setDisabled(disable)

    def block_menus(self, disable: bool) -> None:
        """Desabilita os botões enquanto o worker está rodando."""

        for menu in self.list_menus:
            menu.setDisabled(disable)

    def update_status_bar(self, msg_left: str = "", msg_right: str = ""):
        """Atualiza as duas colunas da statusbar."""

        if msg_left != "":
            self.label_left.setText(msg_left.replace("/", "\\"))
        if msg_right != "":
            self.label_right.setText(msg_right)

    def log_console(self, message):
        self.console.appendPlainText(message)

    def clear_log_console(self):
        self.console.clear()

    def select_db(self, path_db: str = ""):
        """Seleciona o banco de dados .fdb."""

        self.clear_log_console()

        if path_db == "":
            path_db, _ = QFileDialog.getOpenFileName(
                self,
                "Selecionar Banco de Dados",
                "",
                "Firebird Database (*.fdb);;Todos os Arquivos (*)",
            )

        if path_db != "":
            self.db = DataBase(self.server_db, self.user_db, self.password_db, path_db)
            self.update_status_bar(path_db, file_size(path_db))
            self.disable_menus(False)

    def verify_db(self):
        """Cria um worker para verificar o banco de dados.
        \nSe o banco de dados estiver corrompido, pergunta se deseja reparar."""

        self.clear_log_console()
        self.worker = VerifyWorker(self.db)
        self.worker.log_signal.connect(self.log_console)
        self.worker.start()

        self.block_menus(True)
        while self.worker.isRunning():
            QApplication.processEvents()

        if self.worker.db_corrupted:
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle("Banco de Dados Corrompido")
            msgBox.setIcon(QMessageBox.Icon.Warning)
            msgBox.setInformativeText(
                "Banco de Dados Corrompido\nDeseja fazer a Reparação?"
            )
            yes_button = msgBox.addButton("Sim", QMessageBox.ButtonRole.YesRole)
            msgBox.addButton("Não", QMessageBox.ButtonRole.NoRole)
            msgBox.setDefaultButton(yes_button)
            ret = msgBox.exec()

            if msgBox.clickedButton() == yes_button:
                self.repair_db()

        self.block_menus(False)

    def select_restore(self):
        """Seleciona o arquivo .fbk para restaurar."""

        self.clear_log_console()
        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            caption="Selecionar Arquivo FBK",
            filter="Firebird Backup (*.fbk);;Todos os Arquivos (*)",
        )

        if arquivo:
            self.worker = RestoreWorker(
                arquivo, self.server_db, self.user_db, self.password_db
            )
            self.worker.log_signal.connect(self.log_console)
            self.worker.start()

            self.block_menus(True)
            while self.worker.isRunning():
                QApplication.processEvents()

            self.block_menus(False)
            self.select_db(arquivo.split(".")[0] + ".fdb")

    def repair_db(self):
        """Cria um worker para reparar o banco de dados."""

        self.clear_log_console()
        self.worker = RepairWorker(self.db)
        self.worker.log_signal.connect(self.log_console)
        self.worker.start()

        self.block_menus(True)
        while self.worker.isRunning():
            QApplication.processEvents()

        self.update_status_bar(self.db.db_path, file_size(self.db.db_path))
        self.block_menus(False)

    def backup_db(self):
        """Cria um worker para fazer o backup do banco de dados.
        \nPergunta se deseja compactar o backup."""

        self.clear_log_console()
        self.worker = BackupWorker(self.db)
        self.worker.log_signal.connect(self.log_console)
        self.worker.start()

        self.block_menus(True)
        while self.worker.isRunning():
            QApplication.processEvents()

        self.block_menus(False)

        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Backup")
        yes_button = msgBox.addButton("Sim", QMessageBox.ButtonRole.YesRole)
        msgBox.addButton("Não", QMessageBox.ButtonRole.RejectRole)
        msgBox.setIcon(QMessageBox.Icon.Question)
        msgBox.setInformativeText("Compactar o Backup?")
        msgBox.setDefaultButton(yes_button)
        msgBox.exec()

        clicked = msgBox.clickedButton()

        if clicked == yes_button:
            self.log_console(
                f"\nSalvo arquivo Compactado: {zip_file(self.db.fbk_path)}".replace(
                    "/", "\\"
                )
            )

    def open_dialog_user_password(self):
        """Abre o dialog para configurar o Firebird."""

        dialog = UserPasswordDialog(self.server_db, self.user_db, self.password_db)
        if dialog.exec():
            self.server_db, self.user_db, self.password_db = dialog.confirm()

            if self.db is not None:
                self.db.config_user(self.server_db, self.user_db, self.password_db)

            self.clear_log_console()
            self.log_console("Configurações do Firebird Atualizadas!\n")
