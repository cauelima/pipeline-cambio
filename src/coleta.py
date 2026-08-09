# src/coleta.py: etapa E do pipeline
import json
from datetime import datetime, timezone
from pathlib import Path
import requests
URL = "https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL"
RAW_DIR = Path("data/raw")
def coletar_cotacoes() -> dict:
    """Busca as ultimas cotacoes de dolar e euro."""
    resposta = requests.get(URL, timeout=10)
    resposta.raise_for_status()
    return resposta.json()

def salvar_raw(dados: dict) -> Path:
    """Salva a resposta bruta com timestamp UTC no nome."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    carimbo = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    caminho = RAW_DIR / f"cotacoes_{carimbo}.json"
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
    return caminho

if __name__ == "__main__":
    caminho = salvar_raw(coletar_cotacoes())
    print(f"Raw salvo em: {caminho}")


