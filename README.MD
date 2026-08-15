# Pipeline de Câmbio — ETL USD/EUR → BRL

Pipeline de extração, transformação e carga (ETL) que coleta cotações de câmbio (USD e EUR em relação ao BRL) na AwesomeAPI, salva o dado bruto em camada raw, transforma e valida com Pandas, e carrega numa tabela PostgreSQL de forma idempotente.

## Arquitetura

```
AwesomeAPI → coleta.py (ingestão) → data/raw/ (raw, JSON+timestamp)
           → transforma.py (Pandas: normaliza, tipa, valida)
           → pipeline.py (orquestra tudo) → PostgreSQL (tabela cotacoes)
```

## Estrutura do projeto

```
pipeline-cambio-moeda/
├── config.py           # credenciais locais (gitignored)
├── requirements.txt
├── teste.py             # diagnóstico: verifica a conexão com o PostgreSQL
├── src/
│   ├── coleta.py         # E: busca na API e salva raw
│   ├── transforma.py     # T: limpa, tipa, valida
│   └── pipeline.py       # orquestra E + T + L
└── data/
    ├── raw/               # JSON bruto, um por coleta
    └── tratada/            # CSV processado
```

## Como rodar do zero

1. Clonar o repositório e entrar na pasta.
2. Criar e ativar o ambiente virtual:
   ```
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
3. Instalar dependências: `pip install -r requirements.txt`
4. Criar `config.py` na raiz (não versionado) com:
   ```python
   POSTGRES_URL = "postgresql+psycopg2://usuario:senha@localhost:5432/[nome_do_banco]"
   ```
5. Ter um PostgreSQL rodando localmente com o banco criado.
6. (Opcional) Verificar a conexão antes de rodar o pipeline:
   ```
   python teste.py
   ```
   Se a ponte com o banco estiver ok, o script imprime `1`.
7. Rodar o pipeline completo:
   ```
   python src/pipeline.py
   ```

## Decisões técnicas

- **Camada raw imutável**: cada coleta grava um novo JSON com timestamp UTC em `data/raw/`; nunca é editada, só criada e lida.
- **Carga idempotente**: `pipeline.py` reconstrói a tabela inteira a partir de *todos* os raws a cada execução, usando `if_exists="replace"` — rodar o pipeline várias vezes não duplica dados, só incorpora coletas novas.
- **Validação antes da carga**: `transforma.py` interrompe a execução (`raise ValueError`) se faltar coluna obrigatória, houver valor nulo, ou cotação ≤ 0.
- **Segredos fora do Git**: `config.py` guarda a connection string do banco e está no `.gitignore`.

## Evidências de execução

Duas execuções seguidas do pipeline, mostrando que uma nova coleta é incorporada sem duplicar as anteriores (6 raws → 12 linhas, depois 7 raws → 14 linhas):

```
2026-08-14 21:58:25,407 [INFO] pipeline iniciado
2026-08-14 21:58:26,691 [INFO] raw salvo em data\raw\cotacoes_20260815T005826Z.json
2026-08-14 21:58:26,692 [INFO] 6 arquivos raw encontrados
2026-08-14 21:58:26,749 [INFO] validacao ok: 12 linhas integras
2026-08-14 21:58:27,211 [INFO] carga concluida: 12 linhas
2026-08-14 21:58:27,211 [INFO] pipeline concluido com sucesso

2026-08-14 21:59:14,751 [INFO] pipeline iniciado
2026-08-14 21:59:15,128 [INFO] raw salvo em data\raw\cotacoes_20260815T005915Z.json
2026-08-14 21:59:15,128 [INFO] 7 arquivos raw encontrados
2026-08-14 21:59:15,146 [INFO] validacao ok: 14 linhas integras
2026-08-14 21:59:15,401 [INFO] carga concluida: 14 linhas
2026-08-14 21:59:15,401 [INFO] pipeline concluido com sucesso
```