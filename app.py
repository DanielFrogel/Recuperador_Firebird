import tkinter as tk
from tkinter import font
from tkinter import messagebox
from firebird.driver import connect_server, SrvBackupFlag, SrvRestoreFlag, SrvRepairFlag, DatabaseError
from tkinter import filedialog
import datetime
import psutil
from threading import Thread
import os
import zipfile

class BancoDados:
    def __init__(self, user, password):
        self._user = user
        self._password = password
        self._db = ''
        self._db_fbk = ''
        
    def set_db(self, banco_dados):
        fkb_temp = banco_dados.split('.')
        fbk = fkb_temp[0] + '.fbk'             
        self._db = banco_dados
        self._db_fbk = fbk
        
    def set_db_fbk(self, fbk):        
        db_temp = fbk.split('.')
        db = db_temp[0] + '.fdb'                  
        self._db_fbk = fbk  
        self._db = db 
    
    @property
    def db(self):
        return str(self._db)
    
    @property
    def fbk(self):
        return str(self._db_fbk)
    
    @property
    def user(self):
        return str(self._user)
    
    @property
    def password(self):
        return str(self._password)             
    
    def config(self, user, password):
        self._user = user
        self._password = password
        
    def backup_db(self) -> str:
        db_temp = self._db.split('.')
        return f'{db_temp[0]}_backup_{(datetime.date.today()).strftime("%d-%m-%Y")}_{(datetime.datetime.now()).strftime("%H-%M")}.fdb' 

    @property
    def size(self) -> int:
        if os.path.exists(self._db):
            return os.path.getsize(self._db)
        else:
            return 0                         

# Função para retornar em string tamanho do arquivo em kb, mb ou gb
def tamanho_arquivo(arquivo) -> str:
    try:        
        if isinstance(arquivo, str):
            tamanho = os.path.getsize(arquivo) 
        elif isinstance(arquivo, int):
            tamanho = arquivo             
                          
        if tamanho >= 1000000000:
            tamanho_gb = tamanho / (1024 * 1024 * 1024)
            return f'{tamanho_gb:.2f} gb'
        elif tamanho <= 999999:
            tamanho_kb = tamanho / (1024)
            return f'{tamanho_kb:.2f} kb'
        else:
            tamanho_mb = tamanho / (1024 * 1024)
            return f'{tamanho_mb:.2f} mb'                   
    except:
        return

# Função para Zipar arquivos
def zip_arquivo(arquivo):
    try:
        nome_zip = os.path.splitext(arquivo)[0] + '.zip'
        with zipfile.ZipFile(nome_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(arquivo, os.path.basename(arquivo))
            
        return nome_zip
    except PermissionError as e:
        return e

# Função para criar a tela principal
def janela_principal():
    
    def sair():
        if messagebox.askokcancel("Sair", "Tem certeza que deseja sair?"):
            principal.quit()

    def mostrar_sobre():
        messagebox.showinfo("Sobre", "Aplicativo para Recuperação\\Backup de Bancos de Dados em Firebird.")

    def limpa_console():
        console.config(state="normal")
        console.delete("1.0", tk.END)
        console.config(state="disabled")

    # Função para adicionar os textos no Console de retorno da aplicação em negrito ou normal
    def adicionar_console(texto, negrito=False):
        console.config(state="normal")
        bold_font = font.Font(console, console.cget("font"))
        bold_font.configure(weight="bold", size=12)        
        console.tag_configure("bold", font=bold_font)        
       
        if texto and negrito:
            console.insert(tk.END, f"{texto}", 'bold')
            console.config(state="disabled")
            console.yview(tk.END)
        else:
            console.insert(tk.END, f"{texto}")
            console.config(state="disabled")
            console.yview(tk.END)   
    
    # Função para adicionar texto na statusbar2        
    def adiciona_status_bar(banco_dados,tamanho):
        if len(banco_dados) > 45:
            status_bar2.config(text=f'...{(banco_dados[len(banco_dados)-45:len(banco_dados)])} - {tamanho}')
        else:
            status_bar2.config(text=f'{banco_dados} - {tamanho}')                         

    # Função para habilitar e desabilitar menus
    def habilita_desabilita_menus(condicao=bool):   
        if banco.db != '':
            for button in [botao_selecionar, botao_verificar, botao_backup, botao_recuperar, botao_restaurar]:
                button.config(state=("normal" if condicao else "disabled"))
        else:
            for button in [botao_selecionar, botao_restaurar]:
                button.config(state=("normal" if condicao else "disabled"))                    

    # Função para selecionar o banco de dados
    def selecionar_banco():
        banco_dados = banco_dados = str(filedialog.askopenfilename(filetypes=(("Firebird DataBase (*.fdb)", "*.fdb"), ("Todos os arquivos", "*.*")))).replace('/','\\')        
        if banco_dados != '':
            banco.set_db(banco_dados)
            limpa_console()
            adicionar_console('\nBanco de Dados Selecionado:\n\n', True)
            adicionar_console(banco.db)
            adiciona_status_bar(banco.db,tamanho_arquivo(banco.size))            
            habilita_desabilita_menus(True)

    # Função para verificar estado do Banco
    def verificar_banco():        
        limpa_console()                               
        try:                       
            if test_firebird():
                adicionar_console('\nIniciando Verificação de Banco de Dados.....\n\n', True)                 
                habilita_desabilita_menus(False)                
                with connect_server('localhost', user=banco.user, password=banco.password) as srv:                    
                    srv.database.repair(database=banco.db,
                                        flags=SrvRepairFlag.REPAIR | SrvRepairFlag.IGNORE_CHECKSUM | SrvRepairFlag.MEND_DB | SrvRepairFlag.FULL | SrvRepairFlag.CHECK_DB )     
                    retorno = srv.readlines()
                    if len(retorno) == 0:
                        adicionar_console('\nBanco de Dados Ok\n', True) 
                    else:
                        for lst in retorno: 
                            adicionar_console(lst)
                habilita_desabilita_menus(True)                                              
        except DatabaseError as e:
            adicionar_console(e)
            habilita_desabilita_menus(True)                              

    # Cria Thread para melhor execução
    def verificar_banco_thread():               
        thread = Thread(target=verificar_banco)
        thread.start()

    # Função para verificar se Firebird está em execução
    def test_firebird():
        if ("firebird.exe" in (i.name() for i in psutil.process_iter())):
            status_bar1.config(text='Firebird Conectado', fg='green')
            habilita_desabilita_menus(True)          
            return True          
        else:
            status_bar1.config(text='Firebird Desconectado!', fg='red')
            adicionar_console('\n\n- Firebird Desconectado -\n\n-> Verificar Serviço do Firebird\n-> Reiniciar aplicação\n', True) 
            habilita_desabilita_menus(False)             
            return False              
    
    # Função para criar o .fbk do banco       
    def backup_banco():                
        if messagebox.askyesno('Backup da Banco de Dados','Desejar preparar o Banco de Dados?'):
            verificar_banco()           

        if banco.db != '':
            limpa_console()                       
            try:
                if test_firebird():
                    habilita_desabilita_menus(False)
                    with connect_server('localhost', user=banco.user, password=banco.password) as srv:
                        srv.database.backup(database=banco.db,
                                            backup=banco.fbk,
                                            flags=SrvBackupFlag.IGNORE_CHECKSUMS | SrvBackupFlag.NO_GARBAGE_COLLECT | SrvBackupFlag.IGNORE_LIMBO,
                                            stats='TD', verbose=True)  
                        retorno = srv.readline()
                                                                    
                        while retorno != None:
                            adicionar_console(retorno)
                            retorno = srv.readline()
                            
                    habilita_desabilita_menus(True)
                    adicionar_console(f'\n\nCriado Arquivo de Backup:\n\n', True)
                    adicionar_console(f'{banco.fbk}\n\n') 
                    
                    if messagebox.askyesno('Compactar Arquivo', 'Deseja compactar o arquivo de Backup?'):
                        nome_zip = zip_arquivo(banco.fbk)
                        adicionar_console(f'\n\nCriado Arquivo Compactado:\n\n', True)
                        adicionar_console(f'{nome_zip} - {tamanho_arquivo(nome_zip)}\n\n')                                                              
            except DatabaseError as e:
                adicionar_console(e) 
                habilita_desabilita_menus(True)         
    
    # Cria Thread para melhor execução        
    def backup_banco_thread():                              
        thread = Thread(target=backup_banco)
        thread.start()
    
    # Função para restaurar o arquivo .fbk para .fdb        
    def restauracao_banco(): 
        fbk = str(filedialog.askopenfilename(filetypes=(("Firebird Database Backup (*.fbk)", "*.fbk"), ("Todos os arquivos", "*.*")))).replace('/','\\')        
        if fbk != '':
            try:    
                banco.set_db_fbk(fbk)                                                                
                backup = ''
                if test_firebird():
                    if os.path.exists(banco.db):   
                        os.rename(banco.db,banco.backup_db())
                        backup = True                     
                    habilita_desabilita_menus(False) 
                    with connect_server('localhost', user=banco.user, password=banco.password) as srv:
                        srv.database.restore(backup=banco.fbk,
                                            database=banco.db,
                                            flags=SrvRestoreFlag.REPLACE,
                                            stats='TD', verbose=True, page_size=16384)
                        retorno = srv.readline()                                                                
                        while retorno != None:
                            adicionar_console(retorno)
                            retorno = srv.readline()                                                                
                    if backup:
                        adicionar_console('\nCriado Backup:',True)    
                        adicionar_console(f'\n{banco.backup_db()}')    
                    adiciona_status_bar(banco.db,tamanho_arquivo(banco.size))    
                    habilita_desabilita_menus(True)   
                    adicionar_console(f'\n\nCriado Banco de Dados:\n\n', True)                  
                    adicionar_console(f'{banco.db}\n\n')                                      
            except DatabaseError as e:
                adicionar_console(e) 
                habilita_desabilita_menus(True)                
    
    # Cria Thread para melhor execução            
    def restauracao_banco_thread():
        thread = Thread(target=restauracao_banco)
        thread.start()                        
    
    # Função que faz a verificação, backup e restauração em sequência            
    def restaurar_otimizar_banco():
        if banco.db != '':
            if test_firebird():
                verificar_banco()
                try:                                   
                    habilita_desabilita_menus(False) 
                    tamanho_anterior = banco.size                    
                    with connect_server('localhost', user=banco.user, password=banco.password) as srv:
                        srv.database.backup(database=banco.db,
                                            backup=banco.fbk,
                                            flags=SrvBackupFlag.IGNORE_CHECKSUMS | SrvBackupFlag.NO_GARBAGE_COLLECT | SrvBackupFlag.IGNORE_LIMBO,
                                            stats='TD', verbose=True)  
                        retorno = srv.readline()                                                                    
                        while retorno != None:
                            adicionar_console(retorno)
                            retorno = srv.readline() 
                        
                        os.rename(banco.db,banco.backup_db()) 
                                                    
                        srv.database.restore(backup=banco.fbk,
                                            database=banco.db,
                                            flags=SrvRestoreFlag.REPLACE,
                                            stats='TD', verbose=True, page_size=16384)
                        retorno = srv.readline()                                                                
                        while retorno != None:
                            adicionar_console(retorno)
                            retorno = srv.readline()                            

                    adicionar_console(f'\nCriado Backup:\n{banco.backup_db()}', True) 
                    adicionar_console(banco.backup_db()) 
                    adicionar_console('\n\nProcesso de Recuperação\\Otimização Finalizado', True)
                    
                    tamanho_reducao = tamanho_anterior - banco.size                                        
                    if tamanho_reducao > 0:                        
                        adicionar_console(f'\n\nReduzido: {tamanho_arquivo(tamanho_reducao)}\n', True)
                    
                    adiciona_status_bar(banco.db,tamanho_arquivo(banco.size))        
                    habilita_desabilita_menus(True)
                except DatabaseError as e:
                    adicionar_console(e) 
                    habilita_desabilita_menus(True)                                  
     
    # Cria Thread para melhor execução                    
    def restaurar_otimizar_banco_thread():
        thread = Thread(target=restaurar_otimizar_banco)
        thread.start()                                             
        
    # Chama uma janela para inserir o usuário e senha do firebird
    def mudar_usuario_senha():
        def salvar_usuario_senha():            
            banco.config(campo_usuario.get(), campo_senha.get())
            tela_mudar_usuario_senha.destroy()

        tela_mudar_usuario_senha = tk.Toplevel(principal)
        tela_mudar_usuario_senha.title('Login Firebird')
        labels = ["Usuário:", "Senha:"]
        default_values = [banco.user, banco.password]
        for row, (label_text, default_value) in enumerate(zip(labels, default_values)):
            label = tk.Label(tela_mudar_usuario_senha, text=label_text)
            label.grid(row=row, column=0, padx=5, pady=5)
            campo = tk.Entry(tela_mudar_usuario_senha, show="*" if label_text == "Senha:" else "")
            campo.grid(row=row, column=1, padx=5, pady=5)
            campo.insert(0, default_value)
            if label_text == "Senha:":
                campo_senha = campo
            else:
                campo_usuario = campo

        botao_salvar = tk.Button(tela_mudar_usuario_senha, text="Salvar", command=salvar_usuario_senha)
        botao_salvar.grid(row=len(labels), columnspan=2, padx=5, pady=5)


    # Cria a Janela Principal da aplicação
    principal = tk.Tk()
    principal.title("Recuperação de Banco de Dados - Firebird - v1.0")
    principal.resizable(width=False, height=False)
    principal.geometry('500x537')

    # Cria barra de menus
    barra_menu = tk.Menu(principal)

    # Menu Arquivo
    menu_arquivo = tk.Menu(barra_menu, tearoff=0)
    menu_arquivo.add_command(label="Mudar Usuário e Senha", command=mudar_usuario_senha)
    menu_arquivo.add_separator()
    menu_arquivo.add_command(label="Sair", command=sair)
    barra_menu.add_cascade(label="Arquivo", menu=menu_arquivo)

    # Menu Ajuda
    menu_ajuda = tk.Menu(barra_menu, tearoff=0)
    menu_ajuda.add_command(label="Sobre", command=mostrar_sobre)
    barra_menu.add_cascade(label="Ajuda", menu=menu_ajuda)

    # Configurando a barra de menus
    principal.config(menu=barra_menu)

    frame_botoes = tk.Frame(principal)
    frame_botoes.pack()

    status_frame = tk.Frame(principal, bd=1, relief=tk.SUNKEN)
    status_frame.pack(side="bottom", fill=tk.X)

    status_bar1 = tk.Label(status_frame, text="")
    status_bar1.pack(side="left")

    separador = tk.Frame(status_frame, width=1, relief=tk.RAISED, bg="#bfbfbf")
    separador.pack(side="left", padx=10, fill="y")

    status_bar2 = tk.Label(status_frame, text='')
    status_bar2.pack(side="right")

    # Criação dos Botões
    botao_selecionar = tk.Button(frame_botoes, text="Selecionar Banco de Dados", command=selecionar_banco)
    botao_verificar = tk.Button(frame_botoes, text="Verificar", command=verificar_banco_thread, state='disabled')
    botao_backup = tk.Button(frame_botoes, text="Recuperar\\Otimizar", command=restaurar_otimizar_banco_thread, state='disabled')
    botao_recuperar = tk.Button(frame_botoes, text="Backup", command=backup_banco_thread, state='disabled')
    botao_restaurar = tk.Button(frame_botoes, text="Restauração", command=restauracao_banco_thread)

    buttons = [botao_selecionar, botao_verificar, botao_backup, botao_recuperar, botao_restaurar]

    for button in buttons:
        button.pack(side=tk.LEFT, padx=5, pady=2)

    scroll = tk.Scrollbar(principal)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    console = tk.Text(principal, height=30, width=80, state="disabled", wrap="word", yscrollcommand=scroll.set)
    console.pack(expand=True)

    scroll.config(command=console.yview)

    test_firebird()
        
    principal.mainloop()

# Inicia a aplicação e cria a janela principal
if __name__ == '__main__':
    banco = BancoDados(user='SYSDBA', password='masterkey')
    janela_principal()