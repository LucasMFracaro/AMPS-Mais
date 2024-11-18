import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import hashlib

class EntryComFoco(tk.Entry):
    def __init__(self, master=None, botao=None, **kwargs):
        super().__init__(master, **kwargs)
        self.botao = botao
        self.bind("<Return>", self.mudar_foco)

    def mudar_foco(self, event):
        entradas = [entry for entry in self.master.winfo_children() if isinstance(entry, tk.Entry)]
        widget_atual = event.widget
        if isinstance(widget_atual, tk.Entry):
            indice_atual = entradas.index(widget_atual)
            if indice_atual == len(entradas) - 1:
                if self.botao:
                    self.botao.invoke()
            elif indice_atual < len(entradas) - 1:
                entradas[indice_atual + 1].focus()

def connect_db(): return sqlite3.connect('moradores.db')

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS contas_resp 
                    (cpf VARCHAR(11) PRIMARY KEY,
                     senha VARCHAR NOT NULL,
                     nome VARCHAR(50) NOT NULL, 
                     endereco VARCHAR(50) NOT NULL, 
                     cep VARCHAR(8) NOT NULL, 
                     bairro VARCHAR(20) NOT NULL, 
                     cidade VARCHAR(40) NOT NULL, 
                     uf CHAR(2) NOT NULL, 
                     nascimento DATE NOT NULL, 
                     sexo CHAR(1) NOT NULL, 
                     etnia VARCHAR(15) NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS contas_moradores 
                    (cpf_resp VARCHAR(11),
                     parentesco_resp SMALLINT NOT NULL,
                     nome VARCHAR(50) NOT NULL,
                     nascimento DATE NOT NULL,
                     sexo CHAR(1) NOT NULL,
                     etnia VARCHAR(15) NOT NULL,
                     CONSTRAINT fk_contas_resp FOREIGN KEY (cpf_resp) REFERENCES contas_resp(cpf) ON DELETE CASCADE)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS extra_resp 
                    (cpf_resp VARCHAR(11),
                     num_moradores INT NOT NULL,
                     renda_perc DECIMAL(10, 2) NOT NULL,
                     especie_dom CHAR(1) NOT NULL,
                     tipo_dom CHAR(1) NOT NULL,
                     parentesco_resp SMALLINT NOT NULL DEFAULT 1, 
                     CONSTRAINT fk_contas_resp FOREIGN KEY(cpf_resp) REFERENCES contas_resp(cpf) ON DELETE CASCADE)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS menor 
                    (cpf_resp VARCHAR(11), nome VARCHAR(50) NOT NULL,
                     idade SMALLINT NOT NULL, sexo CHAR(1) NOT NULL,
                     educacao_basica VARCHAR(20) NOT NULL,
                     cond_especial VARCHAR(255),
                     CONSTRAINT fk_contas_resp FOREIGN KEY (cpf_resp) REFERENCES contas_resp(cpf) ON DELETE CASCADE)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS idoso
                    (cpf_resp VARCHAR(11), nome VARCHAR(50) NOT NULL,
                     idade SMALLINT NOT NULL, sexo CHAR(1) NOT NULL,
                     aposentado CHAR(3) NOT NULL, bpc CHAR(3),
                     CONSTRAINT fk_contas_resp FOREIGN KEY (cpf_resp) REFERENCES contas_resp(cpf) ON DELETE CASCADE)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS relatorios
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     por_fam FLOAT, 
                     homens INTEGER,
                     mulheres INTEGER,
                     menores INTEGER,
                     idosos INTEGER,
                     pcds INTEGER,
                     populacao_total INTEGER)''')

    conn.commit()
    conn.close()


def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def check_senha(senha_digitada, senha_hash):
    return hash_senha(senha_digitada) == senha_hash

def formatar_entrada(event, tipo="cpf"):
    texto = event.widget.get()
    texto = ''.join(c for c in texto if c.isdigit() or (tipo in ["uf"] and c.isalpha()))
    texto_formatado = ""

    if tipo == "cpf":
        texto_formatado = (
            texto[:3] + ("." if len(texto) > 3 else "") +
            texto[3:6] + ("." if len(texto) > 6 else "") +
            texto[6:9] + ("-" if len(texto) > 9 else "") +
            texto[9:11]
        )
    elif tipo == "data":
        texto_formatado = (
            texto[:2] + ("/" if len(texto) > 2 else "") +
            texto[2:4] + ("/" if len(texto) > 4 else "") +
            texto[4:8]
        )
    elif tipo == "cep":
        texto_formatado = texto[:5] + ("-" if len(texto) > 5 else "") + texto[5:8]
    elif tipo == "uf":
        texto_formatado = texto[:2].upper()
    elif tipo == "num":
        texto_formatado = ''.join(c for c in texto if c.isdigit())

    if event.widget.get() != texto_formatado:
        event.widget.delete(0, tk.END)
        event.widget.insert(0, texto_formatado)



create_tables()

def open_cadastrar():
    cadastrar_window = tk.Toplevel(root)
    cadastrar_window.title("Cadastro")
    cadastrar_window.geometry("600x800")  # Aumentei o tamanho da janela para acomodar mais campos
    cadastrar_window.resizable(False, False)
    
    screen_width = cadastrar_window.winfo_screenwidth()
    screen_height = cadastrar_window.winfo_screenheight()
    
    position_top = int(screen_height / 2 - 800 / 2)
    position_right = int(screen_width / 2 - 600 / 2)
    
    cadastrar_window.geometry(f'800x700+{position_right}+{position_top}')
    
    cadastrar_window.config(bg="#ADD8E6")

    def cadastrar():
        cpf = entry_cpf.get()
        nome = entry_nome.get()
        senha = entry_senha.get()
        endereco = entry_endereco.get()
        cep = entry_cep.get()
        bairro = entry_bairro.get()
        cidade = entry_cidade.get()
        uf = entry_uf.get()
        nascimento = entry_nascimento.get()
        sexo = sexo_var.get()
        etnia = entry_etnia.get()
        num_moradores = entry_num_moradores.get()
        renda_perc = entry_renda_perc.get()
        especie_dom = especie_dom_var.get()
        tipo_dom = tipo_dom_var.get()

        if not cpf or not nome or not senha or not endereco:
            messagebox.showwarning("Atenção", "Todos os campos são obrigatórios!")
            return

        senha_hash = hash_senha(senha)

        conn = connect_db()
        cursor = conn.cursor()

        try:
            create_tables()
            
            cursor.execute("INSERT INTO contas_resp (cpf, senha, nome, endereco, cep, bairro, cidade, uf, nascimento, sexo, etnia) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (cpf, senha_hash, nome, endereco, cep, bairro, cidade, uf, nascimento, sexo, etnia))

            conn.commit()

            cursor.execute("INSERT INTO extra_resp (cpf_resp, num_moradores, renda_perc, especie_dom, tipo_dom) VALUES (?, ?, ?, ?, ?)",
                        (cpf, num_moradores, renda_perc, especie_dom, tipo_dom))

            conn.commit()

            messagebox.showinfo("Cadastro", "Cadastro realizado com sucesso!")
            atualizar_relatorios()
            cadastrar_window.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Erro", "Erro ao cadastrar. Tente novamente.")
            print(e)
        finally:
            conn.close()

    
    tk.Label(cadastrar_window, text="Cadastro de Morador", font=("Arial", 16, "bold"), bg="#ADD8E6").grid(row=0,column=0,columnspan=2,pady=20)

    # Coluna 1 (campo à esquerda)
    tk.Label(cadastrar_window, text="CPF:", bg="#ADD8E6", font=("Arial", 12)).grid(row=1,column=0,padx=10,pady=10,sticky="e")
    entry_cpf = EntryComFoco(cadastrar_window, font=("Arial", 12))
    entry_cpf.grid(row=1,column=1,padx=10,pady=10)
    entry_cpf.bind("<KeyRelease>", lambda event: formatar_entrada(event, tipo="cpf"))

    tk.Label(cadastrar_window, text="Senha:", bg="#ADD8E6", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
    entry_senha = EntryComFoco(cadastrar_window, show="*", font=("Arial", 12))
    entry_senha.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(cadastrar_window, text="Nome:", bg="#ADD8E6", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10, sticky="e")
    entry_nome = EntryComFoco(cadastrar_window, font=("Arial", 12))
    entry_nome.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(cadastrar_window, text="Sexo:", bg="#ADD8E6", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=10, sticky="e")
    sexo_var = tk.StringVar()
    sexo_var.set("")

    radio_sexo_m = tk.Radiobutton(cadastrar_window, text="M", variable=sexo_var, value="M")
    radio_sexo_m.grid(row=4, column=1, padx=10, pady=10, sticky="w")
    radio_sexo_f = tk.Radiobutton(cadastrar_window, text="F", variable=sexo_var, value="F")
    radio_sexo_f.grid(row=4, column=1, padx=52, pady=10, sticky="w")

    tk.Label(cadastrar_window, text="Etnia:", bg="#ADD8E6", font=("Arial", 12)).grid(row=5, column=0, padx=10, pady=10, sticky="e")
    entry_etnia = EntryComFoco(cadastrar_window, font=("Arial", 12))
    entry_etnia.grid(row=5, column=1, padx=10, pady=10)

    tk.Label(cadastrar_window, text="Nascimento:", bg="#ADD8E6", font=("Arial", 12)).grid(row=6, column=0, padx=10, pady=10, sticky="e")
    entry_nascimento = EntryComFoco(cadastrar_window, font=("Arial", 12))
    entry_nascimento.grid(row=6, column=1, padx=10, pady=10)
    entry_nascimento.bind("<KeyRelease>", lambda event: formatar_entrada(event, tipo="data"))

    tk.Label(cadastrar_window, text="Endereço:", bg="#ADD8E6", font=("Arial", 12)).grid(row=7, column=0, padx=10, pady=10, sticky="e")
    entry_endereco = EntryComFoco(cadastrar_window, font=("Arial", 12))
    entry_endereco.grid(row=7, column=1, padx=10, pady=10)

    tk.Label(cadastrar_window, text="CEP:", bg="#ADD8E6", font=("Arial", 12)).grid(row=8, column=0, padx=10, pady=10, sticky="e")
    entry_cep = EntryComFoco(cadastrar_window, font=("Arial", 12))
    entry_cep.grid(row=8, column=1, padx=10, pady=10)
    entry_cep.bind("<KeyRelease>", lambda event: formatar_entrada(event, tipo="cep"))

    tk.Label(cadastrar_window, text="Bairro:", bg="#ADD8E6", font=("Arial", 12)).grid(row=9, column=0, padx=10, pady=10, sticky="e")
    entry_bairro = EntryComFoco(cadastrar_window, font=("Arial", 12))
    entry_bairro.grid(row=9, column=1, padx=10, pady=10)

    tk.Label(cadastrar_window, text="Cidade:", bg="#ADD8E6", font=("Arial", 12)).grid(row=10, column=0, padx=10, pady=10, sticky="e")
    entry_cidade = EntryComFoco(cadastrar_window, font=("Arial", 12))
    entry_cidade.grid(row=10, column=1, padx=10, pady=10)

    tk.Label(cadastrar_window, text="UF:", bg="#ADD8E6", font=("Arial", 12)).grid(row=11, column=0, padx=10, pady=10, sticky="e")
    entry_uf = EntryComFoco(cadastrar_window, font=("Arial", 12))
    entry_uf.grid(row=11, column=1, padx=10, pady=10)
    entry_uf.bind("<KeyRelease>", lambda event: formatar_entrada(event, tipo="uf"))

    tk.Label(cadastrar_window, text="Número de Moradores:", bg="#ADD8E6", font=("Arial", 12)).grid(row=1, column=2, padx=10, pady=10, sticky="e")
    entry_num_moradores = EntryComFoco(cadastrar_window, font=("Arial", 12))
    entry_num_moradores.grid(row=1, column=3, padx=10, pady=10)
    entry_num_moradores.bind("<KeyRelease>", lambda event: formatar_entrada(event, tipo="num"))

    tk.Label(cadastrar_window, text="Renda per Capita:", bg="#ADD8E6", font=("Arial", 12)).grid(row=2, column=2, padx=10, pady=10, sticky="e")
    entry_renda_perc = EntryComFoco(cadastrar_window, font=("Arial", 12))
    entry_renda_perc.grid(row=2, column=3, padx=10, pady=10)
    entry_renda_perc.bind("<KeyRelease>", lambda event: formatar_entrada(event, tipo="num"))

    tk.Label(cadastrar_window, text="Domicílio:", bg="#ADD8E6", font=("Arial", 12)).grid(row=3, column=2, padx=10, pady=10, sticky="e")
    especie_dom_var = tk.StringVar()
    especie_dom_combobox = ttk.Combobox(cadastrar_window, textvariable=especie_dom_var, values=[
        "Próprio com escritura",
        "Particular permanente ocupado",
        "Particular improvisado ocupado",
        "Coletivo com morador"
        ],font=("Arial", 12), state="readonly", width=21)
    especie_dom_combobox.grid(row=3, column=3, padx=10, pady=10)

    tk.Label(cadastrar_window, text="Tipo de Domicílio:", bg="#ADD8E6", font=("Arial", 12)).grid(row=4, column=2, padx=10, pady=10, sticky="e")
    tipo_dom_var = tk.StringVar()
    tipo_dom_combobox = ttk.Combobox(cadastrar_window, textvariable=tipo_dom_var, values=[
        "Casa",
        "Casa de vila ou em condomínio",
        "Apartamento",
        "Casa de cômodos/cortiço",
        "Habitação indígena sem paredes",
        "Estrutura degradada/inacabada"
        ],font=("Arial", 12), state="readonly", width=21)
    tipo_dom_combobox.grid(row=4, column=3, padx=10, pady=10)

    tk.Button(cadastrar_window, text="Cadastrar", command=cadastrar, font=("Arial", 12), bg="#4CAF50", fg="white").grid(row=5, column=0, columnspan=4, pady=10)

def open_cadastrar_idoso():
    cadastrar_idoso_window = tk.Toplevel(root)
    cadastrar_idoso_window.title("Cadastro de Idosos")

    cadastrar_idoso_window.geometry("400x400")
    cadastrar_idoso_window.resizable(False, False)
    cadastrar_idoso_window.config(bg="#ADD8E6")

    screen_width = cadastrar_idoso_window.winfo_screenwidth()
    screen_height = cadastrar_idoso_window.winfo_screenheight()
    window_width = 400
    window_height = 400
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    cadastrar_idoso_window.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    tk.Label(cadastrar_idoso_window, text="Cadastro de Idosos", font=("Arial", 16, "bold"), bg="#ADD8E6").grid(row=0, column=0, columnspan=2, pady=20)

    def cadastrar():
        cpf_resp = entry_cpf.get()
        nome = entry_nome.get()
        idade = entry_idade.get()
        sexo = sexo_var.get()
        aposentado = apos_var.get()
        bpc = bpc_var.get()

        if cpf_resp == "": cpf_resp = CPF # type: ignore

        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT 1 FROM contas_resp WHERE cpf = ?", (cpf_resp,))
            result = cursor.fetchone()

            if not result:
                messagebox.showwarning("CPF não encontrado", "O CPF do responsável não foi encontrado. Verifique e tente novamente.")
                return

            cursor.execute("INSERT INTO idoso (cpf_resp, nome, idade, sexo, aposentado, bpc) VALUES (?, ?, ?, ?, ?, ?)",
                           (cpf_resp, nome, idade, sexo, aposentado, bpc))
            conn.commit()

            messagebox.showinfo("Cadastro", "Cadastro realizado com sucesso!")
            atualizar_relatorios()
            cadastrar_idoso_window.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Erro", "Erro ao cadastrar. Tente novamente.")
            print(e)
        finally:
            conn.close()

    tk.Label(cadastrar_idoso_window, text="CPF do Responsável:", bg="#ADD8E6", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    entry_cpf = EntryComFoco(cadastrar_idoso_window, font=("Arial", 12))
    entry_cpf.grid(row=1, column=1, padx=10, pady=10)
    entry_cpf.bind("<KeyRelease>", lambda event: formatar_entrada(event, tipo="cpf"))
    tk.Label(cadastrar_idoso_window, text="(deixe em branco para usar o do usuário)", bg="#ADD8E6", font=("Arial", 6)).grid(row=2, column=1, padx=20, pady=1, sticky="e")

    tk.Label(cadastrar_idoso_window, text="Nome:", bg="#ADD8E6", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10, sticky="e")
    entry_nome = EntryComFoco(cadastrar_idoso_window, font=("Arial", 12))
    entry_nome.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(cadastrar_idoso_window, text="Idade:", bg="#ADD8E6", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=10, sticky="e")
    entry_idade = EntryComFoco(cadastrar_idoso_window, font=("Arial", 12))
    entry_idade.grid(row=4, column=1, padx=10, pady=10)
    entry_idade.bind("<KeyRelease>", lambda event: formatar_entrada(event, tipo="num"))

    tk.Label(cadastrar_idoso_window, text="Sexo:", bg="#ADD8E6", font=("Arial", 12)).grid(row=5, column=0, padx=10, pady=10, sticky="e")
    sexo_var = tk.StringVar()
    sexo_var.set("")

    radio_sexo_m = tk.Radiobutton(cadastrar_idoso_window, text="M", variable=sexo_var, value="M")
    radio_sexo_m.grid(row=5, column=1, padx=10, pady=10, sticky="w")
    radio_sexo_f = tk.Radiobutton(cadastrar_idoso_window, text="F", variable=sexo_var, value="F")
    radio_sexo_f.grid(row=5, column=1, padx=52, pady=10, sticky="w")

    tk.Label(cadastrar_idoso_window, text="Aposentado?", bg="#ADD8E6", font=("Arial", 12)).grid(row=6, column=0, padx=10, pady=10, sticky="e")
    apos_var = tk.StringVar()
    apos_var.set("")

    radio_apos_s = tk.Radiobutton(cadastrar_idoso_window, text="Sim", variable=apos_var, value="M")
    radio_apos_s.grid(row=6, column=1, padx=10, pady=10, sticky="w")
    radio_apos_n = tk.Radiobutton(cadastrar_idoso_window, text="Não", variable=apos_var, value="F")
    radio_apos_n.grid(row=6, column=1, padx=52, pady=10, sticky="w")

    tk.Label(cadastrar_idoso_window, text="Tem BPC?", bg="#ADD8E6", font=("Arial", 12)).grid(row=7, column=0, padx=10, pady=10, sticky="e")
    bpc_var = tk.StringVar()
    bpc_var.set("")

    radio_bpc_s = tk.Radiobutton(cadastrar_idoso_window, text="Sim", variable=bpc_var, value="M")
    radio_bpc_s.grid(row=7, column=1, padx=10, pady=10, sticky="w")
    radio_bpc_n = tk.Radiobutton(cadastrar_idoso_window, text="Não", variable=bpc_var, value="F")
    radio_bpc_n.grid(row=7, column=1, padx=52, pady=10, sticky="w")


    # Botão de cadastro
    tk.Button(cadastrar_idoso_window, text="Cadastrar", command=cadastrar, font=("Arial", 12), bg="#4CAF50", fg="white").grid(row=8, column=0, columnspan=2, pady=10)



def open_cadastrar_menor():
    cadastrar_menor_window = tk.Toplevel(root)
    cadastrar_menor_window.title("Cadastro de Menores")

    cadastrar_menor_window.geometry("400x400")
    cadastrar_menor_window.resizable(False, False)
    cadastrar_menor_window.config(bg="#ADD8E6")

    screen_width = cadastrar_menor_window.winfo_screenwidth()
    screen_height = cadastrar_menor_window.winfo_screenheight()
    window_width = 400
    window_height = 400
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    cadastrar_menor_window.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    tk.Label(cadastrar_menor_window, text="Cadastro de Menores", font=("Arial", 16, "bold"), bg="#ADD8E6").grid(row=0, column=0, columnspan=2, pady=20)

    def cadastrar():
        cpf_resp = entry_cpf.get()
        parentesco = parentesco_var.get()
        nome = entry_nome.get()
        idade = entry_idade.get()
        sexo = sexo_var.get()
        educacao_basica = educacao_basica_var.get()
        cond_especial = entry_cond_especial.get()

        if cpf_resp == "": cpf_resp = CPF # type: ignore

        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT 1 FROM contas_resp WHERE cpf = ?", (cpf_resp,))
            result = cursor.fetchone()

            if not result:
                messagebox.showwarning("CPF não encontrado", "O CPF do responsável não foi encontrado. Verifique e tente novamente.")
                return

            cursor.execute("INSERT INTO menor (cpf_resp, parentesco, nome, idade, sexo, educacao_basica, cond_especial) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (cpf_resp, parentesco, nome, idade, sexo, educacao_basica, cond_especial))
            conn.commit()

            messagebox.showinfo("Cadastro", "Cadastro realizado com sucesso!")
            atualizar_relatorios()
            cadastrar_menor_window.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Erro", "Erro ao cadastrar. Tente novamente.")
            print(e)
        finally:
            conn.close()

    tk.Label(cadastrar_menor_window, text="CPF do Responsável:", bg="#ADD8E6", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    entry_cpf = EntryComFoco(cadastrar_menor_window, font=("Arial", 12))
    entry_cpf.grid(row=1, column=1, padx=10, pady=10)
    entry_cpf.bind("<KeyRelease>", lambda event: formatar_entrada(event, tipo="cpf"))
    tk.Label(cadastrar_menor_window, text="(deixe em branco para usar o do usuário)", bg="#ADD8E6", font=("Arial", 6)).grid(row=2, column=1, padx=20, pady=1, sticky="e")

    tk.Label(cadastrar_menor_window, text="Parentesco:", bg="#ADD8E6", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
    parentesco_var = tk.StringVar()
    parentesco_combobox = ttk.Combobox(cadastrar_menor_window, textvariable=parentesco_var, values=[
        "Filho(a) do responsável e do cônjuge",
        "Filho(a) somente do responsável"
        ], font=("Arial", 12), state="readonly", width=20)
    parentesco_combobox.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(cadastrar_menor_window, text="Nome:", bg="#ADD8E6", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10, sticky="e")
    entry_nome = EntryComFoco(cadastrar_menor_window, font=("Arial", 12))
    entry_nome.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(cadastrar_menor_window, text="Idade:", bg="#ADD8E6", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=10, sticky="e")
    entry_idade = EntryComFoco(cadastrar_menor_window, font=("Arial", 12))
    entry_idade.grid(row=4, column=1, padx=10, pady=10)
    entry_idade.bind("<KeyRelease>", lambda event: formatar_entrada(event, tipo="num"))

    tk.Label(cadastrar_menor_window, text="Sexo:", bg="#ADD8E6", font=("Arial", 12)).grid(row=5, column=0, padx=10, pady=10, sticky="e")
    sexo_var = tk.StringVar()
    sexo_var.set("")

    radio_sexo_m = tk.Radiobutton(cadastrar_menor_window, text="M", variable=sexo_var, value="M")
    radio_sexo_m.grid(row=5, column=1, padx=10, pady=10, sticky="w")
    radio_sexo_f = tk.Radiobutton(cadastrar_menor_window, text="F", variable=sexo_var, value="F")
    radio_sexo_f.grid(row=5, column=1, padx=52, pady=10, sticky="w")

    tk.Label(cadastrar_menor_window, text="Educação Básica:", bg="#ADD8E6", font=("Arial", 12)).grid(row=6, column=0, padx=10, pady=10, sticky="e")
    educacao_basica_var = tk.StringVar()
    educacao_basica_combobox = ttk.Combobox(cadastrar_menor_window, textvariable=educacao_basica_var, values=[
        "Creche",
        "Pré-Escola",
        "Fundamental",
        "Ensino Médio"
        ], font=("Arial", 12), state="readonly", width=20)
    educacao_basica_combobox.grid(row=6, column=1, padx=10, pady=10)

    tk.Label(cadastrar_menor_window, text="Condição especial:", bg="#ADD8E6", font=("Arial", 12)).grid(row=7, column=0, padx=10, pady=10, sticky="e")
    entry_cond_especial = EntryComFoco(cadastrar_menor_window, font=("Arial", 12))
    entry_cond_especial.grid(row=7, column=1, padx=10, pady=10)

    # Botão de cadastro
    tk.Button(cadastrar_menor_window, text="Cadastrar", command=cadastrar, font=("Arial", 12), bg="#4CAF50", fg="white").grid(row=8, column=0, columnspan=2, pady=10)


def open_cadastrar_morador():
    cadastrar_mor_window = tk.Toplevel(root)
    cadastrar_mor_window.title("Cadastro de Moradores")

    cadastrar_mor_window.geometry("400x400")
    cadastrar_mor_window.resizable(False, False)
    cadastrar_mor_window.config(bg="#ADD8E6")

    screen_width = cadastrar_mor_window.winfo_screenwidth()
    screen_height = cadastrar_mor_window.winfo_screenheight()
    window_width = 400
    window_height = 400
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    cadastrar_mor_window.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    tk.Label(cadastrar_mor_window, text="Cadastro de Morador", font=("Arial", 16, "bold"), bg="#ADD8E6").grid(row=0, column=0, columnspan=2, pady=20)

    def cadastrar():
        cpf_resp = entry_cpf.get()
        nome = entry_nome.get()
        nascimento = entry_nascimento.get()
        sexo = sexo_var.get()
        etnia = entry_etnia.get()

        if cpf_resp == "": cpf_resp = CPF # type: ignore

        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT 1 FROM contas_resp WHERE cpf = ?", (cpf_resp,))
            result = cursor.fetchone()

            if not result:
                messagebox.showwarning("CPF não encontrado", "O CPF do responsável não foi encontrado. Verifique e tente novamente.")
                return
            cursor.execute("INSERT INTO contas_moradores (cpf_resp, nome, nascimento, sexo, etnia) VALUES (?, ?, ?, ?, ?)",
                           (cpf_resp, nome, nascimento, sexo, etnia))
            conn.commit()

            messagebox.showinfo("Cadastro", "Cadastro realizado com sucesso!")
            atualizar_relatorios()
            cadastrar_mor_window.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Erro", "Erro ao cadastrar. Tente novamente.")
            print(e)
        finally:
            conn.close()

    tk.Label(cadastrar_mor_window, text="CPF do Responsável:", bg="#ADD8E6", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    entry_cpf = EntryComFoco(cadastrar_mor_window, font=("Arial", 12))
    entry_cpf.grid(row=1, column=1, padx=10, pady=10)
    entry_cpf.bind("<KeyRelease>", lambda event: formatar_entrada(event, tipo="cpf"))
    tk.Label(cadastrar_mor_window, text="(deixe em branco para usar o do usuário)", bg="#ADD8E6", font=("Arial", 6)).grid(row=2, column=1, padx=20, pady=1, sticky="e")

    tk.Label(cadastrar_mor_window, text="Nome:", bg="#ADD8E6", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10, sticky="e")
    entry_nome = EntryComFoco(cadastrar_mor_window, font=("Arial", 12))
    entry_nome.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(cadastrar_mor_window, text="Sexo:", bg="#ADD8E6", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=10, sticky="e")
    sexo_var = tk.StringVar()
    sexo_var.set("")

    radio_sexo_m = tk.Radiobutton(cadastrar_mor_window, text="M", variable=sexo_var, value="M")
    radio_sexo_m.grid(row=4, column=1, padx=10, pady=10, sticky="w")
    radio_sexo_f = tk.Radiobutton(cadastrar_mor_window, text="F", variable=sexo_var, value="F")
    radio_sexo_f.grid(row=4, column=1, padx=52, pady=10, sticky="w")

    tk.Label(cadastrar_mor_window, text="Etnia:", bg="#ADD8E6", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=10, sticky="e")
    entry_etnia = EntryComFoco(cadastrar_mor_window, font=("Arial", 12))
    entry_etnia.grid(row=5, column=1, padx=10, pady=10)

    tk.Label(cadastrar_mor_window, text="Nascimento:", bg="#ADD8E6", font=("Arial", 12)).grid(row=5, column=0, padx=10, pady=10, sticky="e")
    entry_nascimento = EntryComFoco(cadastrar_mor_window, font=("Arial", 12))
    entry_nascimento.grid(row=6, column=1, padx=10, pady=10)
    entry_nascimento.bind("<KeyRelease>", lambda event: formatar_entrada(event, tipo="data"))

    # Botão de cadastro
    tk.Button(cadastrar_mor_window, text="Cadastrar", command=cadastrar, font=("Arial", 12), bg="#4CAF50", fg="white").grid(row=7, column=0, columnspan=2, pady=10)


def open_forgot_password(): messagebox.showinfo("Esqueci minha Senha", "Por favor, entre em contato com o email: andaime540@gmail.com ou lucasfracaro0403@gmail.com")

def atualizar_relatorios():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS relatorios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        por_fam FLOAT, 
                        homens INTEGER,
                        mulheres INTEGER,
                        menores INTEGER,
                        idosos INTEGER,
                        pcds INTEGER,
                        populacao_total INTEGER
                      )''')

    # Coletando os dados para atualizar, excluindo o CPF '000.000.000-00'
    cursor.execute("SELECT AVG(num_moradores) FROM extra_resp WHERE cpf_resp != '000.000.000-00'")
    por_fam = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM contas_resp WHERE sexo = 'M' AND cpf != '000.000.000-00'")
    homens = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM contas_moradores WHERE sexo = 'M' AND cpf_resp != '000.000.000-00'")
    homens += cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM contas_resp WHERE sexo = 'F' AND cpf != '000.000.000-00'")
    mulheres = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM contas_moradores WHERE sexo = 'F' AND cpf_resp != '000.000.000-00'")
    mulheres += cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM menor WHERE cpf_resp != '000.000.000-00'")
    menores = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM idoso WHERE cpf_resp != '000.000.000-00'")
    idosos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM menor WHERE cond_especial IS NOT NULL AND cond_especial != '' AND cpf_resp != '000.000.000-00'")
    pcds = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM contas_resp WHERE cpf != '000.000.000-00'")
    populacao_total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM contas_moradores WHERE cpf_resp != '000.000.000-00'")
    populacao_total += cursor.fetchone()[0]

    # Atualizando os dados na tabela
    cursor.execute('''UPDATE relatorios 
                      SET por_fam = ?, 
                          homens = ?, 
                          mulheres = ?, 
                          menores = ?, 
                          idosos = ?, 
                          pcds = ?, 
                          populacao_total = ? 
                      WHERE id = 1''', 
                   (por_fam, homens, mulheres, menores, idosos, pcds, populacao_total))

    # Caso não existam registros, insere uma linha com id = 1
    if cursor.rowcount == 0:
        cursor.execute('''INSERT INTO relatorios (id, por_fam, homens, mulheres, menores, idosos, pcds, populacao_total) 
                          VALUES (1, ?, ?, ?, ?, ?, ?, ?)''', 
                       (por_fam, homens, mulheres, menores, idosos, pcds, populacao_total))

    # Commit e fechamento da conexão
    conn.commit()
    conn.close()


def exibir_relatorio():
    conn = connect_db()
    cursor = conn.cursor()
    atualizar_relatorios()

    # Selecionar os dados do relatório
    cursor.execute("SELECT * FROM relatorios")
    relatorio = cursor.fetchone()
    
    if relatorio:
        # Criar nova janela para exibir o relatório
        relatorio_window = tk.Toplevel(root)
        relatorio_window.title("Relatórios")
        relatorio_window.geometry("600x500")
        relatorio_window.resizable(False, False)
        
        # Exibir os dados no formato desejado, incluindo menores, idosos e pcds
        relatorio_text = (
            f"Relatórios:\n\n"
            f"Quantidade de pessoas por família: {relatorio[1]:.2f}\n"
            f"Quantidade de Homens: {relatorio[2]}\n"
            f"Quantidade de Mulheres: {relatorio[3]}\n"
            f"Quantidade de Menores: {relatorio[4]}\n"
            f"Quantidade de Idosos: {relatorio[5]}\n"
            f"Quantidade de PCDs: {relatorio[6]}\n"
            f"População Total: {relatorio[7]}\n"
        )
        
        label_relatorio = tk.Label(relatorio_window, text=relatorio_text, font=("Arial", 12), justify="left")
        label_relatorio.pack(padx=20, pady=20)
    else:
        messagebox.showwarning("Aviso", "Relatório não encontrado. Tente atualizar os dados.")
    
    conn.close()

import tkinter as tk
from tkinter import messagebox

def open_login():
    login_window = tk.Toplevel(root)
    login_window.title("Login")

    # Define o tamanho da janela
    login_window.geometry("400x400")
    login_window.resizable(False, False)
    login_window.config(bg="#ADD8E6")

    # Centraliza a janela
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    window_width = 400
    window_height = 400
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    login_window.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    tk.Label(login_window, text="Login", font=("Arial", 16, "bold"), bg="#ADD8E6").pack(pady=20)

    tk.Label(login_window, text="CPF:", bg="#ADD8E6", font=("Arial", 12)).pack(pady=20)
    entry_cpf = EntryComFoco(login_window, font=("Arial", 12))
    entry_cpf.pack(pady=10)
    entry_cpf.bind("<KeyRelease>", lambda event: formatar_entrada(event, tipo="cpf"))

    btentrar = tk.Button(login_window, text="Entrar", font=("Arial", 12), bg="#4CAF50", fg="white")

    tk.Label(login_window, text="Senha:", bg="#ADD8E6", font=("Arial", 12)).pack(pady=10)
    entry_senha = EntryComFoco(login_window, show="*", font=("Arial", 12), botao=btentrar)
    entry_senha.pack(pady=10)

    btentrar.pack(pady=20)
    btentrar.pack_configure(after=entry_senha)

    # Variáveis para o rodapé
    footer_label = tk.Label(root, text="", font=("Arial", 14, 'bold'), bg="#ADD8E6")
    footer_label.pack(side="bottom", fill="x", pady=10)

    def login():
        cpf = entry_cpf.get()
        senha = entry_senha.get()

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, senha FROM contas_resp WHERE cpf = ?", (cpf,))
        result = cursor.fetchone()

        if result:
            nome = result[0]
            senha_hash = result[1]
            if check_senha(senha, senha_hash):
                messagebox.showinfo("Login", "Login realizado com sucesso!")

                # Atualiza o rodapé com o nome e CPF
                footer_label.config(text=f"Logado como: \n{nome} \n{cpf}")
                globals()["CPF"] = cpf

                login_window.destroy()

                btlogin.pack_forget()
                btcadastro.pack_forget()

                tk.Button(root, text="Cadastrar Morador", command=open_cadastrar_morador, width=20, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=20)
                tk.Button(root, text="Cadastrar Idoso", command=open_cadastrar_idoso, width=20, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=20)
                tk.Button(root, text="Cadastrar Menor de Idade", command=open_cadastrar_menor, width=20, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=20)
                tk.Button(root, text="Relatório", command=exibir_relatorio, width=20, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=20)

            else:
                messagebox.showerror("Erro", "Senha incorreta!")
        else:
            messagebox.showerror("Erro", "CPF não encontrado!")

        conn.close()

    btentrar.config(command=login)
    tk.Button(login_window, text="Esqueci minha Senha", command=open_forgot_password, width=15, font=("Arial", 10), bg="#4CAF50", fg="white").pack(pady=10)



# Tela principal (Hub)
root = tk.Tk()
root.title("Hub de Cadastro")
root.geometry("400x500")
root.resizable(False, False)
root.config(bg="#ADD8E6")

# Centraliza a janela principal
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 400
window_height = 500
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

# Botões do Hub
btlogin = tk.Button(root, text="Login do Responsável", command=open_login, width=20, font=("Arial", 12), bg="#4CAF50", fg="white")
btlogin.pack(pady=20)
btcadastro = tk.Button(root, text="Cadastro de Responsável", command=open_cadastrar, width=20, font=("Arial", 12), bg="#4CAF50", fg="white")
btcadastro.pack(pady=20)

root.mainloop()
