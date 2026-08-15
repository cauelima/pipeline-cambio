# src/mongo_conexao.py: o primeiro documento na nuvem
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from pymongo import MongoClient
from config import MONGO_URL

cliente = MongoClient(MONGO_URL)      # o create_engine do Mongo
banco = cliente["pipeline_cambio"]    # nasce na 1a insercao
colecao = banco["teste"]              # idem: sem CREATE TABLE

resultado = colecao.insert_one({
    "quem": "Caue",
    "aula": 7,
})
print(resultado.inserted_id)

# src/carga_mongo.py: do PostgreSQL para o Atlas
import logging, sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
from sqlalchemy import create_engine
from pymongo import MongoClient

from config import POSTGRES_URL, MONGO_URL

logging.basicConfig(level=logging.INFO,
                     format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def resumir(df: pd.DataFrame) -> list[dict]:
    """Deriva um documento-resumo por moeda."""
    documentos = []
    for moeda, grupo in df.groupby("moeda"):
        recente = grupo.sort_values("data_cotacao").iloc[-1]
        documentos.append({
            "moeda": moeda,
            "ultima_cotacao": float(recente["valor_compra"]),
            "data_ultima": recente["data_cotacao"].isoformat(),
            "media_compra": float(grupo["valor_compra"].mean()),
            "maxima_periodo": float(grupo["maxima_dia"].max()),
        })
    return documentos

def main() -> None:
    engine = create_engine(POSTGRES_URL)
    df = pd.read_sql("SELECT * FROM cotacoes", engine)
    logger.info("%d linhas lidas do PostgreSQL", len(df))

    documentos = resumir(df)

    cliente = MongoClient(MONGO_URL)
    colecao = cliente["pipeline_cambio"]["resumo_cotacoes"]
    colecao.delete_many({})        # o "replace" do mundo Mongo
    colecao.insert_many(documentos)
    logger.info("resumo gravado: %d documentos", len(documentos))
    cliente.close()


if __name__ == "__main__":
    main()