# Análise de Dados de Viagens a Serviço do Governo Federal

## 1. Sobre o projeto

Este projeto foi desenvolvido como parte do desafio avaliativo do curso **Análise de Dados com Python – Módulo 1**. O objetivo foi construir um pipeline ETL (Extração, Transformação e Carga) para analisar dados de viagens a serviço do Governo Federal, utilizando Python e PostgreSQL.

A partir dos dados disponibilizados pelo Portal da Transparência, foram desenvolvidas etapas de extração, tratamento, organização e análise das informações, seguindo a **Arquitetura Medallion**, composta pelas camadas Raw, Silver e Gold.

O projeto contempla dados de viagens, pagamentos, passagens e trechos, permitindo investigar os gastos públicos relacionados aos deslocamentos de servidores e colaboradores a serviço da administração pública.

## 2. Objetivos

- Construir um pipeline ETL utilizando Python e PostgreSQL.
- Aplicar a Arquitetura Medallion para organizar os dados.
- Armazenar os dados originais na camada Raw.
- Realizar limpeza, conversão de tipos e validação dos dados na camada Silver.
- Criar indicadores agregados na camada Gold.
- Utilizar consultas SQL para responder a perguntas de negócio.
- Desenvolver gráficos para facilitar a interpretação dos resultados.

## 3. Tecnologias e ferramentas utilizadas

- **Python:** desenvolvimento do pipeline ETL e das análises.
- **PostgreSQL:** armazenamento e consulta dos dados.
- **SQL:** criação de tabelas, relacionamentos, consultas e indicadores.
- **Pandas:** leitura, manipulação e análise dos dados.
- **Matplotlib:** criação de gráficos.
- **Psycopg2:** conexão e comunicação com o PostgreSQL.
- **Gdown:** download dos arquivos disponibilizados no Google Drive.
- **Jupyter Notebook:** execução e apresentação das análises.
- **Git e GitHub:** versionamento e organização do projeto.

## 4. Fonte de dados

Os dados utilizados foram disponibilizados a partir do Portal da Transparência do Governo Federal, em arquivos CSV compactados em formato ZIP.

Foram utilizados quatro arquivos referentes ao ano de 2025:

- `2025_Viagem.csv`
- `2025_Pagamento.csv`
- `2025_Passagem.csv`
- `2025_Trecho.csv`

Os arquivos apresentam as seguintes características:

- Separador de colunas: ponto e vírgula (`;`).
- Codificação: `latin-1`.
- Valores decimais: vírgula como separador decimal.
- Datas: formato `DD/MM/AAAA`.

## 5. Arquitetura Medallion

O projeto foi organizado em três camadas:

### Raw – Dados brutos

Responsável por armazenar os dados extraídos dos arquivos CSV, preservando os valores originais como texto (`VARCHAR`).

Foram criadas quatro tabelas:

- `raw_viagem`
- `raw_pagamento`
- `raw_passagem`
- `raw_trecho`

A carga é realizada em blocos de 50.000 registros, utilizando o Pandas. Antes de cada nova carga, as tabelas Raw são esvaziadas com `TRUNCATE`, evitando duplicações em novas execuções.

### Silver – Dados tratados

Nesta camada, os dados passam por transformações e conversões de tipos, sendo organizados em tabelas relacionais.

Foram criadas:

- `silver_viagem`
- `silver_pagamento`
- `silver_passagem`
- `silver_trecho`

Principais tratamentos realizados:

- Conversão de valores monetários para `DECIMAL`.
- Conversão de datas para `DATE`.
- Conversão de campos numéricos para seus respectivos tipos.
- Tratamento de valores vazios.
- Cálculo do valor total de cada viagem.
- Cálculo da duração das viagens em dias.
- Aplicação de chaves primárias, chaves estrangeiras e restrições de integridade.

O cálculo do valor total considera:

`valor_total = valor_diarias + valor_passagens + valor_outros_gastos - valor_devolucao`

O valor total é calculado somente quando os quatro componentes estão preenchidos. Caso algum deles esteja ausente, o resultado permanece nulo.

A duração é calculada pela diferença entre a data de fim e a data de início da viagem.

### Gold – Indicadores para análise

A camada Gold foi criada para disponibilizar informações agregadas e facilitar a análise dos dados.

Foram desenvolvidos:

- A VIEW `vw_gold_indicadores`.
- A tabela `gold_indicadores`, criada a partir da consulta à VIEW.

A camada reúne indicadores relacionados a pagamentos, meios de transporte, UFs de destino e órgãos pagadores, utilizando consultas SQL com `JOIN`, `GROUP BY`, funções de agregação e `UNION ALL`.

## 6. Estrutura e execução do projeto

Os principais arquivos desenvolvidos são:

| Arquivo | Responsabilidade |
|---|---|
| `config.py` | Configurações do projeto, caminhos, conexão e parâmetros dos arquivos CSV. |
| `banco.py` | Funções de conexão e execução de comandos no PostgreSQL. |
| `0_criar_banco.py` | Criação e preparação do banco de dados. |
| `0_criar_banco.sql` | Criação das tabelas Raw e Silver. |
| `1_extrair.py` | Download, extração e carregamento dos arquivos CSV na camada Raw. |
| `2_transformar.py` | Transformação dos dados Raw para Silver. |
| `3_analise.ipynb` | Consultas SQL, criação da camada Gold, tabelas e gráficos. |

### Pré-requisitos

Antes de executar o projeto, é necessário ter:

- Python instalado.
- PostgreSQL instalado e em funcionamento.
- Acesso aos arquivos disponibilizados no Google Drive.
- Bibliotecas Python utilizadas no projeto.

Instale as dependências com:

```bash
pip install pandas psycopg2-binary gdown matplotlib jupyter
```

### Configuração da conexão

Configure as credenciais de acesso ao PostgreSQL por meio das variáveis de ambiente utilizadas no arquivo `config.py`.

O banco utilizado pelo projeto é:

```text
transparencia
```

A conexão é centralizada na função `conectar()`, localizada no arquivo `banco.py`.

### Ordem de execução

**1. Criar o banco de dados e as tabelas**

```bash
python 0_criar_banco.py
```

Esse script cria o banco `transparencia` e executa os comandos de criação das tabelas Raw e Silver.

**Atenção:** o script exclui e recria o banco de dados. Portanto, sua execução apaga os dados que já estiverem armazenados nele.

**2. Executar a extração**

```bash
python 1_extrair.py
```

O script realiza o download do arquivo ZIP, extrai os CSVs e carrega os dados nas tabelas Raw.

**3. Executar a transformação**

```bash
python 2_transformar.py
```

Os dados são tratados e carregados nas tabelas Silver, respeitando os relacionamentos entre elas.

**4. Executar as análises**

Abra o Jupyter Notebook:

```bash
jupyter notebook
```

Em seguida, abra e execute o arquivo:

```text
3_analise.ipynb
```

O notebook realiza as consultas SQL, cria a VIEW e a tabela Gold e apresenta os resultados em tabelas e gráficos.

## 7. Análises e perguntas de negócio

Foram desenvolvidas sete análises para investigar os gastos e características das viagens.

### Pergunta 1 – Quais são os cinco órgãos superiores com maior custo total?

O resultado apresentou:

| Órgão | Custo total |
|---|---:|
| Ministério da Justiça e Segurança Pública | R$ 486.933.121,65 |
| Ministério da Defesa | R$ 156.070.304,49 |
| Ministério da Educação | R$ 111.291.349,34 |
| Ministério do Meio Ambiente e Mudança do Clima | R$ 49.697.710,16 |
| Ministério da Previdência Social | R$ 40.417.309,06 |

**Insight:** o Ministério da Justiça e Segurança Pública apresentou o maior custo total entre os órgãos analisados, com aproximadamente R$ 486,9 milhões. O valor é consideravelmente superior ao segundo colocado, o Ministério da Defesa.

### Pergunta 2 – Quais são os três destinos com maior custo médio por viagem?

| Destino | Custo médio |
|---|---:|
| Tejupá | R$ 115.175,00 |
| Chavantes | R$ 114.557,01 |
| Teolândia | R$ 109.322,50 |

**Insight:** os três destinos apresentaram custos médios elevados. Como a média pode ser influenciada por uma quantidade pequena de viagens ou por viagens com valores muito altos, é importante considerar também a quantidade de viagens de cada destino ao interpretar o resultado.

### Pergunta 3 – Qual foi a viagem de maior duração e qual seu custo total?

O resultado encontrado foi:

| Informação | Resultado |
|---|---|
| Órgão | Ministério da Justiça e Segurança Pública |
| Viajante | Informação protegida por sigilo |
| Destinos | Informação protegida por sigilo |
| Data de início | 02/01/2025 |
| Data de término | 15/01/2026 |
| Duração | 378 dias |
| Custo total | R$ 120.650,00 |

**Critério adotado:** inicialmente, a consulta identificava uma viagem com duração maior, mas com valor total igual a zero. Por esse motivo, foi acrescentado o filtro `valor_total > 0`, considerando que uma viagem sem custo registrado poderia não representar uma viagem efetivamente realizada.

Assim, a análise passou a considerar somente viagens com valor total positivo.

Esse filtro representa um critério adotado para a análise, não uma comprovação de que registros com valor zero correspondam necessariamente a viagens não realizadas.

### Pergunta 4 – Qual tipo de pagamento apresenta o maior valor médio?

| Tipo de pagamento | Valor médio |
|---|---:|
| DIÁRIAS | R$ 2.078,28 |

**Insight:** entre os tipos de pagamento analisados, as diárias apresentaram o maior valor médio, seguidas pelas passagens, com média de aproximadamente R$ 1.878,34.

### Pergunta 5 – Qual é o meio de transporte mais utilizado nos trechos?

| Meio de transporte | Quantidade |
|---|---:|
| Veículo Oficial | 386.424 |

**Insight:** o veículo oficial foi o meio de transporte mais utilizado, seguido pelo transporte aéreo, com 232.666 trechos.

### Pergunta 6 – Qual UF de destino apresenta a maior quantidade de trechos?

| UF de destino | Quantidade |
|---|---:|
| São Paulo | 82.722 |

**Insight:** São Paulo foi a UF com maior frequência de trechos de destino, seguida pelo Distrito Federal, com 79.962 registros.

### Pergunta 7 – Qual órgão pagador realizou o maior volume de pagamentos?

| Órgão pagador | Total pago |
|---|---:|
| Fundo Nacional de Segurança Pública | R$ 278.481.047,89 |

**Insight:** o Fundo Nacional de Segurança Pública apresentou o maior valor total de pagamentos entre os órgãos pagadores identificados na análise, seguido pela categoria Sigiloso, com aproximadamente R$ 200,5 milhões.

## 8. Visualizações

Foram desenvolvidos gráficos de barras utilizando Matplotlib para facilitar a interpretação dos indicadores.

As visualizações contemplam:

1. Cinco órgãos superiores com maior custo total.
2. Três destinos com maior custo médio por viagem.
3. Valor médio por tipo de pagamento.
4. Meios de transporte mais utilizados nos trechos.
5. Dez UFs de destino com maior quantidade de trechos.

Os gráficos permitem comparar os resultados, identificar concentrações de gastos e observar padrões de deslocamento.

## 9. Observações sobre a execução

Durante a execução do notebook `3_analise.ipynb`, foi apresentado o seguinte aviso do Pandas:

```text
UserWarning: pandas only supports SQLAlchemy connectable
(engine/connection) or database string URI or sqlite3 DBAPI2 connection.
Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.
```

O aviso está relacionado à utilização de `pd.read_sql()` com uma conexão PostgreSQL criada diretamente pelo `psycopg2`.

Neste projeto, foi utilizada a função `conectar()`, disponibilizada no arquivo `banco.py` como parte da estrutura inicial fornecida. Essa função foi mantida para centralizar a conexão com o banco de dados.

O aviso recomenda a utilização de SQLAlchemy para essa operação, mas não significa, por si só, que as consultas falharam. As consultas utilizadas no notebook foram executadas e retornaram os resultados apresentados.

## 10. Possíveis melhorias futuras

Algumas melhorias que podem ser implementadas em versões futuras:

- Utilizar SQLAlchemy para integração com o Pandas e evitar o aviso apresentado pelo `pd.read_sql()`.
- Implementar logs mais detalhados para acompanhar cada etapa do pipeline.
- Desenvolver validações adicionais para identificar registros inconsistentes.
- Investigar registros com valores zerados ou informações classificadas como inválidas.
- Criar análises temporais para acompanhar a evolução dos gastos ao longo dos meses.
- Desenvolver um dashboard interativo para facilitar a exploração dos indicadores.
- Otimizar as consultas SQL e avaliar índices para melhorar o desempenho.
- Aprimorar o tratamento de valores ausentes e a validação dos dados antes da carga na camada Silver.

## 11. Conclusão

O desenvolvimento deste projeto permitiu aplicar, na prática, conceitos de Engenharia e Análise de Dados, desde a extração de arquivos CSV até a criação de indicadores para responder a perguntas de negócio.

A utilização da Arquitetura Medallion possibilitou organizar o processo em etapas bem definidas: armazenamento dos dados brutos na camada Raw, tratamento e estruturação na Silver e disponibilização de indicadores agregados na Gold.

As análises demonstraram diferenças relevantes entre os gastos dos órgãos, os custos médios por destino, os tipos de pagamento e os meios de transporte utilizados. Também foi possível identificar São Paulo como a UF com maior quantidade de trechos de destino e o Fundo Nacional de Segurança Pública como o órgão pagador com maior volume financeiro na análise.

Além dos resultados, o projeto proporcionou experiência com Python, PostgreSQL, SQL, Pandas, Matplotlib, modelagem relacional e construção de pipelines ETL.

Dessa forma, o desafio contribuiu para consolidar conhecimentos de manipulação, transformação e análise de dados, demonstrando como informações públicas podem ser organizadas e utilizadas para gerar indicadores relevantes sobre os gastos com viagens a serviço do Governo Federal.