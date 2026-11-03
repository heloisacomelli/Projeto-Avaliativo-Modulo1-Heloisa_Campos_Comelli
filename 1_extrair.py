from zipfile import ZipFile
import gdown
from banco import conectar, executar, inserir_em_lote
from config import PASTA_DADOS, DRIVE_FILE_ID, TAMANHO_BLOCO, CSV_SEPARADOR, CSV_ENCODING, ARQUIVOS
import pandas as pd
import os

#====================================================================================================
# Cria a pasta 'data', baixa o arquivo ZIP do Google Drive e extrai os arquivos CSV para dentro dela
#====================================================================================================


def baixar_e_extrair_zip(file_id, nome_zip="viagens_2025_6meses.zip"):
    """Baixa um arquivo .zip do Google Drive via ID e extrai seu conteúdo na pasta 'data'."""

    # Cria a pasta 'data' se ela não existir
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)
    
    # Define o caminho final onde o arquivo .zip será baixado
    caminho_zip = PASTA_DADOS / nome_zip
    
    print("Baixando o arquivo ZIP do Google Drive...")
    try:
        # Baixa o arquivo .zip a partir do ID retirado do link do Google Drive
        gdown.download(id=file_id, output=str(caminho_zip), quiet=False)
        print(f"Arquivo ZIP baixado em: {caminho_zip}")
        
        # Abre o zip e extrai todos os CSVs para dentro da pasta 'data'
        print(f"Extraindo arquivos CSV na pasta {PASTA_DADOS}...")
        
        with ZipFile(caminho_zip, 'r') as zip_ref:
            zip_ref.extractall(PASTA_DADOS)
        print("Extração concluída com sucesso!")
        
        # Remove o .zip deixando apenas os arquivos CSV soltos na pasta data
        caminho_zip.unlink()
        print("Arquivo .zip temporário removido.")
        
    except Exception as e:
        print(f"Ocorreu um erro no processo: {e}")

# Executa o script para o DRIVE_FILE_ID definido no config.py
baixar_e_extrair_zip(DRIVE_FILE_ID)

#=======================================================================================================
# Extrai os dados dos arquivos CSV e insere nas tabelas raw do banco de dados 'transparencia' em blocos
#=======================================================================================================

# Mapeia as colunas de cada arquivo CSV para os nomes das colunas correspondentes das tabelas raw do banco de dados
MAP_VIAGEM = {
    "Identificador do processo de viagem": "id_viagem",
    "Número da Proposta (PCDP)": "num_proposta",
    "Situação": "situacao",
    "Viagem Urgente": "viagem_urgente",
    "Justificativa Urgência Viagem": "justificativa_urgencia_viagem",
    "Código do órgão superior": "cod_orgao_superior",
    "Nome do órgão superior": "nome_orgao_superior",
    "Código órgão solicitante": "cod_orgao_solicitante",
    "Nome órgão solicitante": "nome_orgao_solicitante",
    "CPF viajante": "cpf_viajante",
    "Nome": "nome_viajante",
    "Cargo": "cargo",
    "Função": "funcao",
    "Descrição Função": "descricao_funcao",
    "Período - Data de início": "data_inicio",
    "Período - Data de fim": "data_fim",
    "Destinos": "destinos",
    "Motivo": "motivo",
    "Valor diárias": "valor_diarias",
    "Valor passagens": "valor_passagens",
    "Valor devolução": "valor_devolucao",
    "Valor outros gastos": "valor_outros_gastos"
}

MAP_PAGAMENTO = {
    "Identificador do processo de viagem": "id_viagem",
    "Número da Proposta (PCDP)": "num_proposta",
    "Código do órgão superior": "cod_orgao_superior",
    "Nome do órgão superior": "nome_orgao_superior",
    "Codigo do órgão pagador": "cod_orgao_pagador",
    "Nome do órgao pagador": "nome_orgao_pagador",
    "Código da unidade gestora pagadora": "cod_ug_pagadora",
    "Nome da unidade gestora pagadora": "nome_ug_pagadora",
    "Tipo de pagamento": "tipo_pagamento",
    "Valor": "valor"
}

MAP_PASSAGEM = {
    "Identificador do processo de viagem": "id_viagem",
    "Número da Proposta (PCDP)": "num_proposta",
    "Meio de transporte": "meio_transporte",
    "País - Origem ida": "pais_origem_ida",
    "UF - Origem ida": "uf_origem_ida",
    "Cidade - Origem ida": "cidade_origem_ida",
    "País - Destino ida": "pais_destino_ida",
    "UF - Destino ida": "uf_destino_ida",
    "Cidade - Destino ida": "cidade_destino_ida",
    "País - Origem volta": "pais_origem_volta",
    "UF - Origem volta": "uf_origem_volta",
    "Cidade - Origem volta": "cidade_origem_volta",
    "Pais - Destino volta": "pais_destino_volta",
    "UF - Destino volta": "uf_destino_volta",
    "Cidade - Destino volta": "cidade_destino_volta",
    "Valor da passagem": "valor_passagem",
    "Taxa de serviço": "taxa_servico",
    "Data da emissão/compra": "data_emissao",
    "Hora da emissão/compra": "hora_emissao"
}

MAP_TRECHO = {
    "Identificador do processo de viagem": "id_viagem",
    "Número da Proposta (PCDP)": "num_proposta",
    "Sequência Trecho": "sequencia_trecho",
    "Origem - Data": "origem_data",
    "Origem - País": "origem_pais",
    "Origem - UF": "origem_uf",
    "Origem - Cidade": "origem_cidade",
    "Destino - Data": "destino_data",
    "Destino - País": "destino_pais",
    "Destino - UF": "destino_uf",
    "Destino - Cidade": "destino_cidade",
    "Meio de transporte": "meio_transporte",
    "Número Diárias": "numero_diarias",
    "Missao?": "missao"
}

MAPEAMENTOS = {
    "viagem": MAP_VIAGEM,
    "pagamento": MAP_PAGAMENTO,
    "passagem": MAP_PASSAGEM,
    "trecho": MAP_TRECHO
}

def carregar_csv(tipo_arquivo):
    """
    Realiza a carga dos dados de um arquivo CSV para sua respectiva tabela RAW no PostgreSQL, utilizando inserção em lotes.
    """

    arquivo = ARQUIVOS[tipo_arquivo]
    nome_csv = arquivo["csv"]
    nome_csv = os.path.join("data", nome_csv)
    tabela = arquivo["tabela_raw"]
    mapeamento = MAPEAMENTOS[tipo_arquivo]

    colunas_csv = list(mapeamento.keys())
    colunas_postgres = list(mapeamento.values())

    # Monta o comando INSERT
    campos = ", ".join(f'"{coluna}"' for coluna in colunas_postgres)
    valores = ", ".join(["%s"] * len(colunas_postgres))

    sql_insert = f"""
        INSERT INTO {tabela} ({campos})
        VALUES ({valores})
    """

    conexao = conectar()
    total_registros = 0

    try:
        cursor = conexao.cursor()
        
        print(f"Limpando tabela {tabela}...")
        cursor.execute(f"TRUNCATE TABLE {tabela}")
        conexao.commit()
        cursor.close()

        for df in pd.read_csv(
            nome_csv,
            sep=CSV_SEPARADOR,
            encoding=CSV_ENCODING,
            chunksize=TAMANHO_BLOCO,
            dtype=str,
            keep_default_na=False,
            na_filter=False
        ):

            # Remove espaços extras no início e no final dos nomes das colunas
            df.columns = df.columns.str.strip()

            faltando = set(colunas_csv) - set(df.columns)

            if faltando:
                raise ValueError(f"Colunas não encontradas no arquivo {nome_csv}: {faltando}")

            df = df[colunas_csv]
            df = df.rename(columns=mapeamento)

            # Converte o DataFrame em lista de tuplas
            linhas = list(df.itertuples(index=False, name=None))

            inserir_em_lote(conexao, sql_insert, linhas)

            total_registros += len(linhas)

            print(f"{tabela}: {total_registros} registros carregados...")

        print(f"\nCarga finalizada: {tabela}")
        print(f"Total de registros: {total_registros}")

    except Exception as erro:
        conexao.rollback()
        print(f"Erro ao carregar {nome_csv}: {erro}")
        raise

    finally:
        conexao.close()

    return total_registros

for tipo_arquivo in ARQUIVOS:
    print(f"\nIniciando carga: {tipo_arquivo}")
    carregar_csv(tipo_arquivo)

print("\n Fase 1 concluída com sucesso!")