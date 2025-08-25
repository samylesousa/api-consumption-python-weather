from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd
import matplotlib.pyplot as plt



#função para retirar caracteres especiais e acentos dos nomes das cidades
def slugify(cidade: str) -> str:
    string_nova = "".join(caracter.lower() if caracter.isalnum() else " " for caracter in cidade)

    string_nova = string_nova.split()

    return "-".join(string_nova)

def lendo_cidade(banco_path: str | Path, cidade: str) -> pd.DataFrame:
    with sqlite3.connect(banco_path) as conn:
        dados = pd.read_sql_query(
            "SELECT cidade, latitude, longitude, timestamp, temperatura, umidade, velocidade_vento"
            " FROM tempo_por_horas WHERE cidade = ? ORDER BY timestamp",
            conn,
            params=(cidade,),
            parse_dates=["timestamp"]
        )

        return dados

def plotando_temperatura(dados: pd.DataFrame, cidade: str, output_path: str | Path) -> str:
    
    #criando o diretório em casos em que ele não existe
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    #o slugify transforma o nome da cidade em uma versão sem acentos ou caracteres diferentes
    imagem_path = output_path / f"temperatura_por_tempo_{slugify(cidade)}.png"

    plt.figure()
    plt.plot(dados["timestamp"], dados["temperatura"])
    plt.title(f"Temperatura da {cidade} ao longo do tempo")
    plt.xlabel("Tempo")
    plt.ylabel("Temperatura (C)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(imagem_path, dpi=150)
    plt.close()

    return str(imagem_path)

def plotando_temperatura_diaria(dados: pd.DataFrame, cidade: str, output_path: str | Path) -> str:
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    imagem_path = output_path / f"temperatura_diaria_{slugify(cidade)}.png"

    dados_copia = dados.copy()
    dados_copia["data"] = dados_copia["timestamp"].dt.date
    diaria = dados_copia.groupby("data", as_index=False)["temperatura"].mean()

    plt.figure()
    plt.plot(diaria["data"], diaria["temperatura"])
    plt.title(f"Média diária da temperatura da cidade {cidade}")
    plt.xlabel("Dia")
    plt.ylabel("Temperatura média (C)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(imagem_path, dpi=150)
    plt.close()

    return str(imagem_path)