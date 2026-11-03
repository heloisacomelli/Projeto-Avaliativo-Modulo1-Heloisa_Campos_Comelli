from decimal import Decimal, InvalidOperation
from datetime import datetime
import pandas as pd

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
    if valor is None or str(valor).strip() == "":
        return None

    valor = str(valor).strip()

    try:
        return int(valor)
    except ValueError:
        raise ValueError(f"Valor inteiro inválido: {valor}")

