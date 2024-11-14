# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib

def connect_db():
    return sqlite3.connect('moradores.db')

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
                    (tem_menor SMALLINT NOT NULL DEFAULT 0,
                     cpf_resp VARCHAR(11), idade SMALLINT,
                     creche BOOLEAN, pre_escola BOOLEAN,
                     fundamental BOOLEAN, ensino_medio BOOLEAN,
                     condicao_especial VARCHAR(255),
                     CONSTRAINT fk_contas_resp FOREIGN KEY (cpf_resp) REFERENCES contas_resp(cpf) ON DELETE CASCADE)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS idoso
                    (tem_idoso SMALLINT NOT NULL DEFAULT 0,
                     cpf_resp VARCHAR(11), idade SMALLINT,
                     aposentado BOOLEAN, bpc BOOLEAN,Casa
                     CONSTRAINT fk_contas_resp FOREIGN KEY (cpf_resp) REFERENCES contas_resp(cpf) ON DELETE CASCADE)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS relatorios
                    (por_fam FLOAT, homens INTEGER,
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

def atualizar_relatorios():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(num_moradores) FROM extra_resp")
    por_fam = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM contas_resp WHERE sexo = 'M'")
    homens = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM contas_moradores WHERE sexo = 'M'")
    homens += cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM contas_resp WHERE sexo = 'F'")
    mulheres = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM contas_moradores WHERE sexo = 'F'")
    mulheres += cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM menor")
    menores = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM idoso")
    idosos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM menor WHERE condicao_especial IS NOT NULL AND condicao_especial != ''")
    pcds = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM contas_resp")
    populacao_total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM contas_moradores")
    populacao_total += cursor.fetchone()[0]
    cursor.execute("DELETE FROM relatorios")
    cursor.execute('''INSERT INTO relatorios (por_fam, homens, mulheres, menores, idosos, pcds, populacao_total) VALUES (?, ?, ?, ?, ?, ?, ?)''', (por_fam, homens, mulheres, menores, idosos, pcds, populacao_total))
    conn.commit()
    conn.close()

create_tables()

def open_register():
    register_window = tk.Toplevel(root)
    register_window.title("Cadastrar-se")
    register_window.geometry("600x800")  # Aumentei o tamanho da janela para acomodar mais campos
    register_window.resizable(False, False)
    
    screen_width = register_window.winfo_screenwidth()
    screen_height = register_window.winfo_screenheight()
    
    position_top = int(screen_height / 2 - 800 / 2)
    position_right = int(screen_width / 2 - 600 / 2)
    
    register_window.geometry(f'800x700+{position_right}+{position_top}')
    
    register_window.config(bg="#ADD8E6")

    def cadastrar():
        cpf = entry_cpf.get()
        nome = entry_nome.get()
        senha = entry_senha.get()
        endereco = entry_endereco.get()
        cep = entry_cep.get()
        bairro = entry_bairro.get()
        cidade = entry_cidade.get()
        uf = entry_uf.get()
        nascimento = entry_nascimento.get()  # Adicionando campo de nascimento
        sexo = entry_sexo.get()  # Sexo M/F
        etnia = entry_etnia.get()  # Etnia
        num_moradores = entry_num_moradores.get()
        renda_perc = entry_renda_perc.get()
        especie_dom = entry_especie.get()  # Usando Entry para espécie de domicílio
        tipo_dom = entry_tipo.get()  # Usando Entry para tipo de domicílio

        if not cpf or not nome or not senha or not endereco:
            messagebox.showwarning("Atenção", "Todos os campos são obrigatórios!")
            return

        senha_hash = hash_senha(senha)

        conn = connect_db()
        cursor = conn.cursor()

        try:
            # Criar as tabelas se não existirem
            create_tables()
            
            # Inserir os dados na tabela 'contas_resp'
            cursor.execute("INSERT INTO contas_resp (cpf, senha, nome, endereco, cep, bairro, cidade, uf, nascimento, sexo, etnia) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (cpf, senha_hash, nome, endereco, cep, bairro, cidade, uf, nascimento, sexo, etnia))

            conn.commit()

            # Inserir dados adicionais na tabela 'extra_resp'
            cursor.execute("INSERT INTO extra_resp (cpf_resp, num_moradores, renda_perc, especie_dom, tipo_dom) VALUES (?, ?, ?, ?, ?)",
                        (cpf, num_moradores, renda_perc, especie_dom, tipo_dom))

            conn.commit()

            messagebox.showinfo("Cadastro", "Cadastro realizado com sucesso!")
            atualizar_relatorios()
            register_window.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Erro", "Erro ao cadastrar. Tente novamente.")
            print(e)
        finally:
            conn.close()

    
    tk.Label(register_window, text="Cadastro de Morador", font=("Arial", 16, "bold"), bg="#ADD8E6").grid(row=0,column=0,columnspan=2,pady=20)

    # Coluna 1 (campo à esquerda)
    tk.Label(register_window, text="CPF:", bg="#ADD8E6", font=("Arial", 12)).grid(row=1,column=0,padx=10,pady=10,sticky="e")
    entry_cpf = tk.Entry(register_window, font=("Arial", 12))
    entry_cpf.grid(row=1,column=1,padx=10,pady=10)

    tk.Label(register_window, text="Nome:", bg="#ADD8E6", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
    entry_nome = tk.Entry(register_window, font=("Arial", 12))
    entry_nome.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(register_window, text="Etnia:", bg="#ADD8E6", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10, sticky="e")
    entry_etnia = tk.Entry(register_window, font=("Arial", 12))
    entry_etnia.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(register_window, text="Nascimento:", bg="#ADD8E6", font=("Arial", 12)).grid(row=11, column=0, padx=10, pady=10, sticky="e")
    entry_nascimento = tk.Entry(register_window, font=("Arial", 12))
    entry_nascimento.grid(row=11, column=1, padx=10, pady=10)
  
    tk.Label(register_window, text="Sexo (M/F):", bg="#ADD8E6", font=("Arial", 12)).grid(row=4, column=0, padx=10, pady=10, sticky="e")
    entry_sexo = tk.Entry(register_window, font=("Arial", 12))
    entry_sexo.grid(row=4, column=1, padx=10, pady=10)

    tk.Label(register_window, text="Senha:", bg="#ADD8E6", font=("Arial", 12)).grid(row=5, column=0, padx=10, pady=10, sticky="e")
    entry_senha = tk.Entry(register_window, show="*", font=("Arial", 12))
    entry_senha.grid(row=5, column=1, padx=10, pady=10)

    tk.Label(register_window, text="Endereço:", bg="#ADD8E6", font=("Arial", 12)).grid(row=6, column=0, padx=10, pady=10, sticky="e")
    entry_endereco = tk.Entry(register_window, font=("Arial", 12))
    entry_endereco.grid(row=6, column=1, padx=10, pady=10)

    tk.Label(register_window, text="CEP:", bg="#ADD8E6", font=("Arial", 12)).grid(row=7, column=0, padx=10, pady=10, sticky="e")
    entry_cep = tk.Entry(register_window, font=("Arial", 12))
    entry_cep.grid(row=7, column=1, padx=10, pady=10)

    tk.Label(register_window, text="Bairro:", bg="#ADD8E6", font=("Arial", 12)).grid(row=8, column=0, padx=10, pady=10, sticky="e")
    entry_bairro = tk.Entry(register_window, font=("Arial", 12))
    entry_bairro.grid(row=8, column=1, padx=10, pady=10)

    tk.Label(register_window, text="Cidade:", bg="#ADD8E6", font=("Arial", 12)).grid(row=9, column=0, padx=10, pady=10, sticky="e")
    entry_cidade = tk.Entry(register_window, font=("Arial", 12))
    entry_cidade.grid(row=9, column=1, padx=10, pady=10)

    tk.Label(register_window, text="UF:", bg="#ADD8E6", font=("Arial", 12)).grid(row=10, column=0, padx=10, pady=10, sticky="e")
    entry_uf = tk.Entry(register_window, font=("Arial", 12))
    entry_uf.grid(row=10, column=1, padx=10, pady=10)

    # Coluna 2 (campo à direita) - Adicionando novos campos
    tk.Label(register_window, text="Número de Moradores:", bg="#ADD8E6", font=("Arial", 12)).grid(row=1, column=2, padx=10, pady=10, sticky="e")
    entry_num_moradores = tk.Entry(register_window, font=("Arial", 12))
    entry_num_moradores.grid(row=1, column=3, padx=10, pady=10)

    tk.Label(register_window, text="Renda per Capita:", bg="#ADD8E6", font=("Arial", 12)).grid(row=2, column=2, padx=10, pady=10, sticky="e")
    entry_renda_perc = tk.Entry(register_window, font=("Arial", 12))
    entry_renda_perc.grid(row=2, column=3, padx=10, pady=10)

    # Espécie de Domicílio (na segunda coluna) - Usando Entry
    tk.Label(register_window, text="Espécie de Domicílio:", bg="#ADD8E6", font=("Arial", 12)).grid(row=3, column=2, padx=10, pady=10, sticky="e")
    entry_especie = tk.Entry(register_window, font=("Arial", 12))
    entry_especie.grid(row=3, column=3, padx=10, pady=10)

    # Tipo de Domicílio (na segunda coluna) - Usando Entry
    tk.Label(register_window, text="Tipo de Domicílio:", bg="#ADD8E6", font=("Arial", 12)).grid(row=4, column=2, padx=10, pady=10, sticky="e")
    entry_tipo = tk.Entry(register_window, font=("Arial", 12))
    entry_tipo.grid(row=4, column=3, padx=10, pady=10)

    tk.Button(register_window, text="Cadastrar", command=cadastrar, font=("Arial", 12), bg="#4CAF50", fg="white").grid(row=5, column=0, columnspan=4, pady=20)

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

    tk.Label(login_window, text="CPF:", bg="#ADD8E6", font=("Arial", 12)).pack(pady=10)
    entry_cpf = tk.Entry(login_window, font=("Arial", 12))
    entry_cpf.pack(pady=10)

    tk.Label(login_window, text="Senha:", bg="#ADD8E6", font=("Arial", 12)).pack(pady=10)
    entry_senha = tk.Entry(login_window, show="*", font=("Arial", 12))
    entry_senha.pack(pady=10)

    # Função de login
    def login():
        cpf = entry_cpf.get()
        senha = entry_senha.get()

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT senha FROM contas_resp WHERE cpf = ?", (cpf,))
        result = cursor.fetchone()

        if result:
            senha_hash = result[0]
            if check_senha(senha, senha_hash):
                messagebox.showinfo("Login", "Login realizado com sucesso!")
            else:
                messagebox.showerror("Erro", "Senha incorreta!")
        else:
            messagebox.showerror("Erro", "CPF não encontrado!")

        conn.close()

    tk.Button(login_window, text="Entrar", command=login, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=20)

# Funo de recuperao de senha
def open_forgot_password():
    messagebox.showinfo("Esqueci minha Senha", "Por favor, entre em contato com o email: andaime540@gmail.com")

# Tela principal (Hub)
root = tk.Tk()
root.title("Hub de Cadastro")
root.geometry("400x400")
root.resizable(False, False)
root.config(bg="#ADD8E6")

# Centraliza a janela principal
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 400
window_height = 400
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

# Botes do Hub
tk.Button(root, text="Login", command=open_login, width=20, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=20)
tk.Button(root, text="Cadastrar-se", command=open_register, width=20, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=20)
tk.Button(root, text="Esqueci minha Senha", command=open_forgot_password, width=20, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=20)

# Inicia a interface grfica
root.mainloop()
