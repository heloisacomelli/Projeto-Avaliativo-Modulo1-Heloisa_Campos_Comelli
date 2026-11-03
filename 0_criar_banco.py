import psycopg2
from banco import conectar, executar
from config import POSTGRES_CONFIG

#=========================================================================================
# Cria o banco de dados 'transparencia' com a exclusão prévia do banco caso ele já exista
#=========================================================================================

def conectar_banco_padrao():
    """
    Conecta ao PostgreSQL usando o database padrao (postgres) e retorna a conexao.
    """
    config_temporaria = POSTGRES_CONFIG.copy()
    config_temporaria['dbname'] = 'postgres'

    # Ativa o autocommit obrigatório para CREATE/DROP DATABASE 
    try:
        conexao = psycopg2.connect(**config_temporaria)
        conexao.autocommit = True
        return conexao
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados padrão: {e}")
        exit(1)

try:
    conexao = conectar_banco_padrao()
    cursor = conexao.cursor()

    # Derruba qualquer outra conexão ativa no banco transparencia
    print("Encerrando conexões ativas no banco 'transparencia'...")
    sql_fechar_conexoes = """
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = 'transparencia'
          AND pid <> pg_backend_pid();
    """
    executar(conexao, sql_fechar_conexoes)

    executar(conexao, "DROP DATABASE IF EXISTS transparencia;")
    print("Criando o banco de dados 'transparencia'...")
    executar(conexao, "CREATE DATABASE transparencia ENCODING 'UTF8';")
    print("Banco de dados 'transparencia' criado com sucesso.")

except Exception as e:
    print(f"Erro ao criar o banco de dados: {e}")

finally:
    if cursor:
        cursor.close()
    if conexao:
        conexao.close()
