import tkinter as tk
from tkinter import messagebox
import modelos.firebird as firebird

"""
    Cria a Janela Principal e os menus

    a parte de trabalhar com o banco de dados está no firebird.py

"""


def janela_principal():
    def sair():
        if messagebox.askokcancel("Sair", "Tem certeza que deseja sair?"):
            principal.quit()

    def mostrar_sobre():
        messagebox.showinfo("Sobre", "Aplicativo para Recuperação\\Backup de Bancos de Dados em Firebird.")

    # Função para adicionar os textos no Console de retorno da aplicação
    def adicionar_console(texto):
        console.config(state="normal")
        if texto:
            console.insert(tk.END, f"{texto}\n")
            console.config(state="disabled")
            console.yview(tk.END)

    def selecionar_banco():
        if banco := firebird.selecionar_banco():
            adicionar_console(f'Banco de Dados Selecionado: {banco}')
            status_bar2.config(text=banco)

    def selecionar_firebird():
        messagebox.showinfo("Mensagem","Firebird Encontrado") if firebird.selecionar_firebird() else messagebox.showwarning("Mensagem","Firebird Não Encontrado")
        habilita_desabilita_menus()

    def verificar_banco():
        adicionar_console(firebird.verificar_banco())

    def habilita_desabilita_menus():
        firebird_instalado = firebird.verifica_instalacao_firebird()
        status_bar1.config(text="Firebird Conectado" if firebird_instalado else "Firebird Desconectado!")
        for button in [botao_selecionar, botao_verificar, botao_backup, botao_recuperar, botao_restaurar]:
            button.config(state="normal" if firebird_instalado else "disabled")

    def backup_banco():
        verificar_banco()
        adicionar_console(firebird.backup_banco_dados())

    def restauracao_banco():
        adicionar_console(firebird.restaurar_banco_dados())

    def restaurar_otimizar_banco():
        verificar_banco()
        adicionar_console(firebird.backup_banco_dados())
        adicionar_console(firebird.restaurar_banco_dados())
        adicionar_console(firebird.verificar_banco())
        adicionar_console('\n\nProcesso de Recuperação\\Otimização Finalizado')

    # Chama uma janela para inserir o usuário e senha do firebird
    def mudar_usuario_senha():
        def salvar_usuario_senha():
            firebird.usuario_firebird = campo_usuario.get()
            firebird.password_firebird = campo_senha.get()
            tela_mudar_usuario_senha.destroy()

        tela_mudar_usuario_senha = tk.Toplevel(principal)
        tela_mudar_usuario_senha.title('Login Firebird')
        labels = ["Usuário:", "Senha:"]
        default_values = ["SYSDBA", "masterkey"]
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
    menu_arquivo.add_command(label="Selecionar Firebird", command=selecionar_firebird)
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
    botao_verificar = tk.Button(frame_botoes, text="Verificar", command=verificar_banco)
    botao_backup = tk.Button(frame_botoes, text="Recuperar\\Otimizar", command=restaurar_otimizar_banco)
    botao_recuperar = tk.Button(frame_botoes, text="Backup", command=backup_banco)
    botao_restaurar = tk.Button(frame_botoes, text="Restauração", command=restauracao_banco)

    buttons = [botao_selecionar, botao_verificar, botao_backup, botao_recuperar, botao_restaurar]

    for button in buttons:
        button.pack(side=tk.LEFT, padx=5, pady=2)

    scroll = tk.Scrollbar(principal)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    console = tk.Text(principal, height=30, width=80, state="disabled", wrap="word", yscrollcommand=scroll.set)
    console.pack(expand=True)

    scroll.config(command=console.yview)

    habilita_desabilita_menus()

    principal.mainloop()
