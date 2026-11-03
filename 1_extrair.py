from zipfile import ZipFile
import gdown
from banco import conectar, executar, inserir_em_lote
from config import PASTA_DADOS, DRIVE_FILE_ID, TAMANHO_BLOCO, ARQUIVOS
import pandas as pd

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

