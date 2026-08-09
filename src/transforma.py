# src/transforma.py: etapa T do pipeline
import json, logging
from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
TRATADA_DIR = Path("data/tratada")

logging.basicConfig(level=logging.INFO,
                     format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def listar_raws() -> list[Path]:
    return sorted(RAW_DIR.glob("cotacoes_*.json"))


def carregar_raw(caminho: Path) -> dict:
    with open(caminho, encoding="utf-8") as arq:
        return json.load(arq)

def transformar(dados: dict, origem: str) -> pd.DataFrame:
    """Achata o dict de dicts em DataFrame limpo e tipado."""
    registros = list(dados.values())
    df = pd.DataFrame(registros)
 
    df = df[["code", "codein", "bid", "ask", "high", "low", "create_date"]]

    df = df.rename(columns={
        "code": "moeda",
        "codein": "moeda_destino",
        "bid": "valor_compra",
        "ask": "valor_venda",
        "high": "maxima_dia",
        "low": "minima_dia",
        "create_date": "data_cotacao"
    })

    numericas = ["valor_compra", "valor_venda", "maxima_dia", "minima_dia"]
    for coluna in numericas:
        df[coluna] = df[coluna].astype(float)

    df["data_cotacao"] = pd.to_datetime(df["data_cotacao"])

    df["arquivo_origem"] = origem
    return df


#""Barra dado ruim. Levanta ValueError se algo nao fizer sentido."""
def validar(df: pd.DataFrame) -> None:
    obrigatorias = ["moeda", "valor_compra", "valor_venda", "data_cotacao"]
    for coluna in obrigatorias:
        if not coluna in df.columns:
            raise ValueError(f"coluna ausente: {coluna}")
        if df[coluna].isnull().any():
            raise ValueError(f"coluna com nulo: {coluna}")
    if (df["valor_compra"] <= 0).any():
        raise ValueError("cotacao <= 0: dado suspeito, carga abortada")
    logger.info("validacao ok: %d linhas integras", len(df))


if __name__ == "__main__":
    arquivos = listar_raws()
    if not arquivos:
        raise SystemExit("nenhum raw: rode src/coleta.py antes")

    logger.info("%d arquivos raw encontrados", len(arquivos))

    tabelas = []
    for caminho in arquivos:
        dados = carregar_raw(caminho)
        tabelas.append(transformar(dados, origem=caminho.name))

    df = pd.concat(tabelas, ignore_index=True)
    validar(df)

    TRATADA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(TRATADA_DIR / "cotacoes.csv", index=False)
    logger.info("tratada gravada (%d linhas)", len(df))