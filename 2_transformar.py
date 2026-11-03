from decimal import Decimal, InvalidOperation
from datetime import datetime
from banco import conectar, executar, inserir_em_lote
from config import TAMANHO_BLOCO

#=====================================================================================================
# Define as funções de limpeza de dados para cada tipo de dado específico (monetário, data e inteiro)
#=====================================================================================================

def limpar_decimal(valor):
    """Converte valores monetários para Decimal. Retorna None quando o valor estiver vazio."""
    if valor is None or valor.strip() == "":
        return None

    valor = valor.strip().replace(".", "").replace(",", ".")

    try:
        return Decimal(valor)
    except InvalidOperation:
        raise ValueError(f"Valor monetário inválido: {valor}")

def limpar_data(valor):
    """Converte datas para o formato date. Retorna None quando o valor estiver vazio."""
    if valor is None or valor.strip() == "":
        return None

    return datetime.strptime(valor.strip(), "%d/%m/%Y").date()

def limpar_inteiro(valor):
    """ Converte um valor para inteiro (int). Retorna None se o valor estiver vazio ou for None."""
    if valor is None or str(valor).strip() == "":
        return None

    valor = str(valor).strip()

    try:
        return int(valor)
    except ValueError:
        raise ValueError(f"Valor inteiro inválido: {valor}")

#====================================================================================================================================
# Realiza as transformações necessárias nos dados das tabelas raw e insere os dados transformados nas tabelas silver correspondentes
#====================================================================================================================================

# Limpa as tabelas silver antes de iniciar a transformação e adição dos dados transformados
def limpar_tabelas_silver():
    """
    Limpa as tabelas SILVER antes de iniciar uma nova transformação.
    O CASCADE também limpa as tabelas dependentes por chave estrangeira.
    """

    conexao = conectar()

    sql = """
        TRUNCATE TABLE
            silver_pagamento,
            silver_passagem,
            silver_trecho,
            silver_viagem
        CASCADE;
    """

    try:
        executar(conexao, sql)
        print("Tabelas silver limpas com sucesso!")

    finally:
        conexao.close()

# Realiza a transformação dos dados da tabela raw_viagem e os insere na tabela silver_viagem
def transformar_silver_viagem():
    """
    Lê os dados da raw_viagem, realiza as transformações
    necessárias e insere os resultados na silver_viagem.
    """

    # Uma conexão para leitura e outra para escrita
    conexao_leitura = conectar()
    conexao_escrita = conectar()

    cursor = None
    total_registros = 0

    sql_select = """
        SELECT
            id_viagem,
            num_proposta,
            situacao,
            viagem_urgente,
            cod_orgao_superior,
            nome_orgao_superior,
            nome_viajante,
            cargo,
            data_inicio,
            data_fim,
            destinos,
            motivo,
            valor_diarias,
            valor_passagens,
            valor_devolucao,
            valor_outros_gastos
        FROM raw_viagem
    """

    sql_insert = """
        INSERT INTO silver_viagem (
            id_viagem,
            num_proposta,
            situacao,
            viagem_urgente,
            cod_orgao_superior,
            nome_orgao_superior,
            nome_viajante,
            cargo,
            data_inicio,
            data_fim,
            destinos,
            motivo,
            valor_diarias,
            valor_passagens,
            valor_devolucao,
            valor_outros_gastos,
            valor_total,
            duracao_dias
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """

    try:
        # Cria o cursor para consultar a tabela raw
        cursor = conexao_leitura.cursor(name="cursor_viagem")

        cursor.execute(sql_select)

        while True:

            # Busca um bloco de registros da tabela raw
            registros = cursor.fetchmany(TAMANHO_BLOCO)

            if not registros:
                break

            linhas_silver = []

            for registro in registros:

                (
                    id_viagem,
                    num_proposta,
                    situacao,
                    viagem_urgente,
                    cod_orgao_superior,
                    nome_orgao_superior,
                    nome_viajante,
                    cargo,
                    data_inicio,
                    data_fim,
                    destinos,
                    motivo,
                    valor_diarias,
                    valor_passagens,
                    valor_devolucao,
                    valor_outros_gastos
                ) = registro

                # Conversão das datas
                data_inicio = limpar_data(data_inicio)
                data_fim = limpar_data(data_fim)

                # Conversão dos valores monetários
                valor_diarias = limpar_decimal(valor_diarias)
                valor_passagens = limpar_decimal(valor_passagens)
                valor_devolucao = limpar_decimal(valor_devolucao)
                valor_outros_gastos = limpar_decimal(valor_outros_gastos)

                # Cálculo do valor total
                valores = [
                    valor_diarias,
                    valor_passagens,
                    valor_devolucao,
                    valor_outros_gastos
                ]

                if all(valor is not None for valor in valores):
                    valor_total = (
                        valor_diarias
                        + valor_passagens
                        + valor_outros_gastos
                        - valor_devolucao
                    )
                else:
                    valor_total = None

                # Cálculo da duração da viagem
                if data_inicio is not None and data_fim is not None:
                    duracao_dias = (data_fim - data_inicio).days
                else:
                    duracao_dias = None

                # Monta a linha com os dados transformados
                linhas_silver.append((
                    id_viagem,
                    num_proposta,
                    situacao,
                    viagem_urgente,
                    cod_orgao_superior,
                    nome_orgao_superior,
                    nome_viajante,
                    cargo,
                    data_inicio,
                    data_fim,
                    destinos,
                    motivo,
                    valor_diarias,
                    valor_passagens,
                    valor_devolucao,
                    valor_outros_gastos,
                    valor_total,
                    duracao_dias
                ))

            # Insere o bloco na tabela SILVER
            inserir_em_lote(
                conexao_escrita,
                sql_insert,
                linhas_silver
            )

            total_registros += len(linhas_silver)

            print(
                f"silver_viagem: {total_registros} registros transformados..."
            )

        print("\nTransformação finalizada!")
        print(f"Total de registros: {total_registros}")

    except Exception as erro:

        conexao_leitura.rollback()
        conexao_escrita.rollback()

        print(f"Erro na transformação da silver_viagem: {erro}")
        raise

    finally:

        if cursor is not None:
            cursor.close()

        conexao_leitura.close()
        conexao_escrita.close()

# Realiza a transformação dos dados da tabela raw_pagamento e os insere na tabela silver_pagamento
def transformar_silver_pagamento():
    """
    Lê os dados da raw_pagamento, realiza as transformações
    necessárias e insere os resultados na silver_pagamento.
    """

    conexao_leitura = conectar()
    conexao_escrita = conectar()

    cursor = None
    total_registros = 0

    sql_select = """
        SELECT
            id_viagem,
            num_proposta,
            nome_orgao_pagador,
            nome_ug_pagadora,
            tipo_pagamento,
            valor
        FROM raw_pagamento
    """

    sql_insert = """
        INSERT INTO silver_pagamento (
            id_viagem,
            num_proposta,
            nome_orgao_pagador,
            nome_ug_pagadora,
            tipo_pagamento,
            valor
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    try:
        cursor = conexao_leitura.cursor(name="cursor_pagamento")
        cursor.execute(sql_select)

        while True:
            registros = cursor.fetchmany(TAMANHO_BLOCO)

            if not registros:
                break

            linhas_silver = []

            for registro in registros:

                (
                    id_viagem,
                    num_proposta,
                    nome_orgao_pagador,
                    nome_ug_pagadora,
                    tipo_pagamento,
                    valor
                ) = registro

                # Conversão do valor monetário
                valor = limpar_decimal(valor)

                linhas_silver.append((
                    id_viagem,
                    num_proposta,
                    nome_orgao_pagador,
                    nome_ug_pagadora,
                    tipo_pagamento,
                    valor
                ))

            # Insere o bloco na tabela SILVER
            inserir_em_lote(
                conexao_escrita,
                sql_insert,
                linhas_silver
            )

            total_registros += len(linhas_silver)

            print(
                f"silver_pagamento: {total_registros} registros transformados..."
            )

        print("\nTransformação da silver_pagamento finalizada!")
        print(f"Total de registros: {total_registros}")

    except Exception as erro:
        conexao_leitura.rollback()
        conexao_escrita.rollback()

        print(f"Erro na transformação da silver_pagamento: {erro}")
        raise

    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass

        conexao_leitura.close()
        conexao_escrita.close()

# Realiza a transformação dos dados da tabela raw_passagem e os insere na tabela silver_passagem
def transformar_silver_passagem():
    """
    Lê os dados da raw_passagem, realiza as transformações
    necessárias e insere os resultados na silver_passagem.
    """

    conexao_leitura = conectar()
    conexao_escrita = conectar()

    cursor = None
    total_registros = 0

    sql_select = """
        SELECT
            id_viagem,
            num_proposta,
            meio_transporte,
            pais_origem_ida,
            uf_origem_ida,
            cidade_origem_ida,
            pais_destino_ida,
            uf_destino_ida,
            cidade_destino_ida,
            valor_passagem,
            taxa_servico,
            data_emissao
        FROM raw_passagem
    """

    sql_insert = """
        INSERT INTO silver_passagem (
            id_viagem,
            num_proposta,
            meio_transporte,
            pais_origem_ida,
            uf_origem_ida,
            cidade_origem_ida,
            pais_destino_ida,
            uf_destino_ida,
            cidade_destino_ida,
            valor_passagem,
            taxa_servico,
            data_emissao
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
    """

    try:
        cursor = conexao_leitura.cursor(name="cursor_passagem")
        cursor.execute(sql_select)

        while True:
            registros = cursor.fetchmany(TAMANHO_BLOCO)

            if not registros:
                break

            linhas_silver = []

            for registro in registros:

                (
                    id_viagem,
                    num_proposta,
                    meio_transporte,
                    pais_origem_ida,
                    uf_origem_ida,
                    cidade_origem_ida,
                    pais_destino_ida,
                    uf_destino_ida,
                    cidade_destino_ida,
                    valor_passagem,
                    taxa_servico,
                    data_emissao
                ) = registro

                # Conversão dos valores monetários
                valor_passagem = limpar_decimal(valor_passagem)
                taxa_servico = limpar_decimal(taxa_servico)

                # Conversão da data de emissão
                data_emissao = limpar_data(data_emissao)

                linhas_silver.append((
                    id_viagem,
                    num_proposta,
                    meio_transporte,
                    pais_origem_ida,
                    uf_origem_ida,
                    cidade_origem_ida,
                    pais_destino_ida,
                    uf_destino_ida,
                    cidade_destino_ida,
                    valor_passagem,
                    taxa_servico,
                    data_emissao
                ))

            # Insere o bloco na tabela SILVER
            inserir_em_lote(
                conexao_escrita,
                sql_insert,
                linhas_silver
            )

            total_registros += len(linhas_silver)

            print(
                f"silver_passagem: {total_registros} registros transformados..."
            )

        print("\nTransformação da silver_passagem finalizada!")
        print(f"Total de registros: {total_registros}")

    except Exception as erro:
        conexao_leitura.rollback()
        conexao_escrita.rollback()

        print(f"Erro na transformação da silver_passagem: {erro}")
        raise

    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass

        conexao_leitura.close()
        conexao_escrita.close()

# Realiza a transformação dos dados da tabela raw_trecho e os insere na tabela silver_trecho
def transformar_silver_trecho():
    """
    Lê os dados da raw_trecho, realiza as transformações
    necessárias e insere os resultados na silver_trecho.
    """

    conexao_leitura = conectar()
    conexao_escrita = conectar()

    cursor = None
    total_registros = 0

    sql_select = """
        SELECT
            id_viagem,
            sequencia_trecho,
            origem_data,
            origem_uf,
            origem_cidade,
            destino_data,
            destino_uf,
            destino_cidade,
            meio_transporte,
            numero_diarias
        FROM raw_trecho
    """

    sql_insert = """
        INSERT INTO silver_trecho (
            id_viagem,
            sequencia_trecho,
            origem_data,
            origem_uf,
            origem_cidade,
            destino_data,
            destino_uf,
            destino_cidade,
            meio_transporte,
            numero_diarias
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
    """

    try:
        cursor = conexao_leitura.cursor(name="cursor_trecho")
        cursor.execute(sql_select)

        while True:
            registros = cursor.fetchmany(TAMANHO_BLOCO)

            if not registros:
                break

            linhas_silver = []

            for registro in registros:

                (
                    id_viagem,
                    sequencia_trecho,
                    origem_data,
                    origem_uf,
                    origem_cidade,
                    destino_data,
                    destino_uf,
                    destino_cidade,
                    meio_transporte,
                    numero_diarias
                ) = registro

                # Conversão da sequência para inteiro
                sequencia_trecho = limpar_inteiro(sequencia_trecho)

                # Conversão das datas
                origem_data = limpar_data(origem_data)
                destino_data = limpar_data(destino_data)

                # Conversão do número de diárias
                numero_diarias = limpar_decimal(numero_diarias)

                linhas_silver.append((
                    id_viagem,
                    sequencia_trecho,
                    origem_data,
                    origem_uf,
                    origem_cidade,
                    destino_data,
                    destino_uf,
                    destino_cidade,
                    meio_transporte,
                    numero_diarias
                ))

            # Insere o bloco na tabela SILVER
            inserir_em_lote(
                conexao_escrita,
                sql_insert,
                linhas_silver
            )

            total_registros += len(linhas_silver)

            print(
                f"silver_trecho: {total_registros} registros transformados..."
            )

        print("\nTransformação da silver_trecho finalizada!")
        print(f"Total de registros: {total_registros}")

    except Exception as erro:
        conexao_leitura.rollback()
        conexao_escrita.rollback()

        print(f"Erro na transformação da silver_trecho: {erro}")
        raise

    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass

        conexao_leitura.close()
        conexao_escrita.close()

# Função para executar todas as funções transformar_silver_* em sequência, garantindo que as dependências sejam respeitadas
def executar_transformacoes():
    """
    Executa todas as transformações das tabelas RAW para SILVER.
    Primeiro limpa as tabelas SILVER e depois realiza as cargas.
    """

    print("\nIniciando processo de transformação...")

    # Limpa as tabelas SILVER
    limpar_tabelas_silver()

    # Executa as transformações na ordem das dependências
    transformar_silver_viagem()

    transformar_silver_pagamento()

    transformar_silver_passagem()

    transformar_silver_trecho()

    print("\nTodas as transformações foram concluídas!")

if __name__ == "__main__":
    executar_transformacoes()
    print("\n Fase 2 concluída com sucesso!")