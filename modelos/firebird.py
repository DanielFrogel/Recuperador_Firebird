from pathlib import Path
from tkinter import filedialog
import os
import psutil
import time
import datetime

"""

    Conexão e verificação de instalação do firebird e do banco de dados

"""

# Variáveis que serão utilizadas pelas várias funções
caminho_firebird = Path('C:\\Program Files (x86)\\Firebird\\Firebird_3_0\\')
banco_dados = ''
banco_fbk = ''
pasta_log = os.path.expandvars('%appdata%\\recuperador_firebird')
usuario_firebird = 'SYSDBA'
password_firebird = 'masterkey'
mensagem_gbak = 'Problemas ao realizar GBak, verificar usuário/senha e se Banco de Dados não está em uso'

# Crie o diretório se não existir
os.makedirs(pasta_log, exist_ok=True)

# Selecionar a pasta instalação Firebird
def selecionar_firebird():
    global caminho_firebird 
    
    caminho_firebird = Path(str(filedialog.askdirectory()).replace('/','\\')) 

    if verifica_instalacao_firebird():
        return True
    else:          
        return False

# Verifica se na pasta seleciona está o firebird.exe
def verifica_instalacao_firebird():
    caminho_firebird_executavel = Path(str(caminho_firebird) + '\\firebird.exe')
    
    if caminho_firebird_executavel.exists():
        return True
    else:
        return False           

# Função para selecionar o banco de dados se ainda não foi selecionado     
def selecionar_banco():
    global banco_dados
    global usuario_firebird
    global password_firebird    
      
    if len(str(banco_dados)) == 0:
        banco_dados = str(filedialog.askopenfilename(filetypes=(("Firebird DataBase (*.fdb)", "*.fdb"), ("Todos os arquivos", "*.*")))).replace('/','\\')
    
    if len(str(banco_dados)) != 0:
        return str(banco_dados)

# Função que faz verificação da estrutura e prepara o banco para backup
def verificar_banco():
    global banco_dados
    global pasta_log 
    global usuario_firebird
    global password_firebird       

    arquivo_bat = os.path.join(pasta_log, 'verificar.bat')
        
    if len(str(banco_dados)) != 0:
        with open(arquivo_bat, 'w') as arquivo:
            arquivo.write(f'''
echo off
cls
path="{caminho_firebird}"
set ISC_USER={usuario_firebird}
set ISC_PASSWORD={password_firebird}
gfix -v -full "{banco_dados}"
gfix -mend -full -ignore "{banco_dados}" 
gfix -v -full "{banco_dados}" & gfix -v -full "{banco_dados}" > {pasta_log}\\log.log
IF %ERRORLEVEL% NEQ 0 (echo Problemas ao realizar Gfix, verificar usuário/senha e se Banco de Dados não está em uso) > {pasta_log}\\log.log                    
                        ''')        
        try:
            os.startfile(arquivo_bat) 
            
            time.sleep(1)
            
            while ("gfix.exe" in (i.name() for i in psutil.process_iter())):
                time.sleep(1)
            
            time.sleep(1)
            
            arquivo_log = os.path.join(pasta_log, 'log.log')

            with open(arquivo_log, 'r') as arquivo: 
                log = str(arquivo.read())
                if len(log) == 0:
                    return '\n*--------------------- Verificação ---------------------*\n\nVerificação de Estrutura Ok\n'
                else:
                    return f'\n*--------------------- Verificação ---------------------*\n\nErro ao executar Verificação\n\n{log}\n\nImportante Fazer a Recuperação!'
        except Exception as e:
            return f'\n\nErro ao executar Verificação\n\nErro: {e}'                         
    else:
        return 'Banco de Dados Inválido\n'
    

# Função de que o backup do banco da dados
def backup_banco_dados():
    global banco_dados
    global pasta_log 
    global banco_fbk 
    global usuario_firebird
    global password_firebird      

    arquivo_bat = os.path.join(pasta_log, 'backup.bat')
    banco_fbk_temp = str(banco_dados).split('.')       
    banco_fbk = banco_fbk_temp[0] + '.fbk'
        
    if len(banco_dados) != 0:
        with open(arquivo_bat, 'w') as arquivo:
            arquivo.write(f'''
echo off
cls
path="{caminho_firebird}"
set ISC_USER={usuario_firebird}
set ISC_PASSWORD={password_firebird}
gbak -backup -v -ignore -l -g "{banco_dados}" "{banco_fbk}" & gbak -backup -v -ignore -l -g "{banco_dados}" "{banco_fbk}" > {pasta_log}\\log.log                     
IF %ERRORLEVEL% NEQ 0 (echo {mensagem_gbak}) > {pasta_log}\\log.log
                        ''')  
        try:
            os.startfile(arquivo_bat)                                     
            
            arquivo_log = os.path.join(pasta_log, 'log.log')
            
            time.sleep(1)
            
            while ("gbak.exe" in (i.name() for i in psutil.process_iter())):                               
                time.sleep(1)                          

            with open(arquivo_log, 'r') as arquivo: 
                log = str(arquivo.read())
                return f'\n*----------------------- Backup -----------------------*\n\n{log}\n\nBackup Finalizado.\nSalvo em: {banco_fbk}'if log != (mensagem_gbak + '\n') else f'\n*----------------------- Backup -----------------------*\n\n{log}\n'
        except Exception as e:
            return f'\n\nErro ao executar Backup\n\nErro: {e}'                       
    else:
        return '\n\nBanco de Dados Inválido\n'            

# Função que faz o restore do banco de dados e renomeia o banco de dados anterior
def restaurar_banco_dados():
    global banco_dados
    global pasta_log 
    global banco_fbk 
    global usuario_firebird
    global password_firebird      

    # Caminho do arquivo com expansão de variável de ambiente
    arquivo_bat = os.path.join(pasta_log, 'restaurar.bat')
    
    if len(banco_fbk) == 0:
        banco_fbk = str(filedialog.askopenfilename(filetypes=(("Firebird DataBase Backup (*.fbk)", "*.fbk"), ("Todos os arquivos", "*.*")))).replace('/','\\')
    
    banco_dados_temp = str(banco_fbk).split('.')
    banco_dados = Path(banco_dados_temp[0]+'.fdb')
        
    if len(banco_fbk) != 0:
        with open(arquivo_bat, 'w') as arquivo:
            arquivo.write(f'''
echo off
cls
path="{caminho_firebird}"
set ISC_USER={usuario_firebird}
set ISC_PASSWORD={password_firebird}
gbak -v -p 16384 -rep "{banco_fbk}" "{banco_dados}" & gbak -v -p 16384 -rep "{banco_fbk}" "{banco_dados}" > {pasta_log}\\log.log
IF %ERRORLEVEL% NEQ 0 (echo Problemas ao realizar GBak, verificar usuário/senha e banco de dados) > {pasta_log}\\log.log                       
                        ''')  
        try:
            if banco_dados.exists():
                os.rename(str(banco_dados),str((banco_dados_temp[0]+f'_backup_{(datetime.date.today()).strftime("%d-%m-%Y")}_{(datetime.datetime.now()).strftime("%H-%M")}.fdb')))            
            
            os.startfile(arquivo_bat) 
            
            time.sleep(1)
            
            while ("gbak.exe" in (i.name() for i in psutil.process_iter())):
                time.sleep(1)              
            
            arquivo_log = os.path.join(pasta_log, 'log.log')
            
            with open(arquivo_log, 'r') as arquivo: 
                log = str(arquivo.read())
                if banco_dados.exists():
                    banco_fbk = ''
                    return f'\n*--------------------- Recuperação ---------------------*\n\n{log}\n\nRestauração Finalizado.\nSalvo em: {banco_dados}'
                else:
                    banco_fbk = ''
                    return f'{log}\n\nProblema da Criação do Banco de Dados:\n {banco_dados}'

                    
        except Exception as e:
            return f'\n\nErro ao executar Restauração\n\nErro: {e}'                      
    else:
        return '\n\nBackup de Banco de Dados Inválido\n' 
 
    