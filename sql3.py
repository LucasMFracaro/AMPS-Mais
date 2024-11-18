import sqlite3
import sys
from prettytable import PrettyTable

def conectar_banco(nome_db):
    try:
        # Conecta ao banco de dados SQLite
        conexao = sqlite3.connect(nome_db)
        return conexao
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        sys.exit(1)

def executar_comando(conexao, comando):
    try:
        # Cria um cursor para execução dos comandos
        cursor = conexao.cursor()
        
        # Comando DESCRIBE
        if comando.lower().startswith("describe "):
            nome_tabela = comando.split()[1]
            comando_pragmas = f"PRAGMA table_info({nome_tabela});"
            cursor.execute(comando_pragmas)
            resultados = cursor.fetchall()
            
            # Exibe a descrição da tabela
            print(f"\nDescrição da tabela '{nome_tabela}':\n")
            tabela = PrettyTable()
            tabela.field_names = ["ID", "Nome", "Tipo", "Não Nulo", "Valor Padrão", "Chave"]
            for linha in resultados:
                tabela.add_row(linha)
            print(tabela)
        
        # Comando SELECT com PrettyTable
        elif comando.strip().upper().startswith("SELECT"):
            cursor.execute(comando)
            resultados = cursor.fetchall()
            
            if resultados:
                # Cria uma tabela bonitinha para exibir os resultados
                colunas = [desc[0] for desc in cursor.description]
                tabela = PrettyTable(colunas)
                for linha in resultados:
                    tabela.add_row(linha)
                print(tabela)
            else:
                print("Nenhum resultado encontrado.")
        
        # Outros comandos como INSERT, UPDATE, DELETE
        else:
            cursor.execute(comando)
            conexao.commit()
            print("Comando executado com sucesso.")
            
    except sqlite3.Error as e:
        print(f"Erro ao executar o comando: {e}")

def menu_interativo():
    print("SQLite3 CMD - Console Interativo")
    print("Digite 'exit' para sair.")
    
    nome_db = input("Digite o nome do banco de dados SQLite (ex: banco.db): ")
    conexao = conectar_banco(nome_db)
    
    while True:
        # Exibe o prompt
        comando = input("sqlite3> ")
        
        # Comando de saída
        if comando.lower() == 'exit':
            print("Saindo do SQLite3 CMD...")
            conexao.close()
            break
        
        # Executa o comando
        executar_comando(conexao, comando)

if __name__ == "__main__":
    menu_interativo()
