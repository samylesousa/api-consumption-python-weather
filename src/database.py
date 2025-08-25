from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


# função que cria o diretório caso ele não exista
def verificando_diretorios(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def inicializar_banco(banco_path: str | Path) -> None:
    """Inicializa o banco de dados, cria a tabela e os atributos"""

    banco_path = Path(banco_path)
    verificando_diretorios(banco_path)

    with sqlite3.connect(banco_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tempo_por_horas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cidade TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                timestamp TEXT NOT NULL,
                temperatura REAL,
                umidade REAL,
                velocidade_vento REAL,
                UNIQUE(cidade, timestamp) ON CONFLICT REPLACE
            )
            """
        )

        #criando um indice para organizar a tabela com uma chave de unicidade (cidade, timestamp)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cidade_tempo ON tempo_por_horas(cidade, timestamp)")


# função que prepara os dados para armazenar no banco de dados
def formatacao_banco(
        cidade, 
        latitude, 
        longitude, 
        time, 
        temperatura, 
        umidade, 
        velocidade_vento
):
    return (
        cidade,
        latitude,
        longitude,
        time.isoformat(),
        float(temperatura) if temperatura is not None else None,
        float(umidade) if umidade is not None else None,
        float(velocidade_vento) if velocidade_vento is not None else None,
    )
    



def operacoes_por_horas(
        banco_path: str | Path,
        cidade: str,
        latitude: float,
        longitude: float,
        dados: pd.DataFrame,
) -> int:
    
    """Insere ou atualiza linhas baseados em parâmetros como cidade.
    Além disso retorna a quantidade de linhas que foram escritas."""

    linhas = [
        formatacao_banco(cidade, latitude, longitude, time, temperatura, umidade, velocidade_vento)
        for time, temperatura, umidade, velocidade_vento in zip(dados["timestamp"], dados["temperatura"], dados["umidade"], dados["velocidade_vento"])
    ]

    with sqlite3.connect(banco_path) as conn:
        cursor = conn.executemany(
            """
            INSERT INTO tempo_por_horas
            (cidade, latitude, longitude, timestamp, temperatura, umidade, velocidade_vento)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(cidade, timestamp) DO UPDATE SET
                latitude = excluded.latitude,
                longitude = excluded.longitude,
                temperatura = excluded.temperatura,
                umidade = excluded.umidade,
                velocidade_vento = excluded.velocidade_vento;
            """,
            linhas
        )
        
        return cursor.rowcount or 0