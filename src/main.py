from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

from src.api_client import geocode_cidade, buscar_clima_horario, ApiError
from src.database import inicializar_banco, operacoes_por_horas
from src.analysis import lendo_cidade, plotando_temperatura, plotando_temperatura_diaria

def analisar_argumentos() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Pipeline de dados climáticos")
    p.add_argument("--cidades", type=str, default="Fortaleza, São Paulo",
                   help="Lista de cidades separadas por vírgula.")
    p.add_argument("--dias", type=int, default=7,
                   help="Quantos dias (contando o dia atual) devem ser coletados")
    p.add_argument("--banco_path", type=Path, default=Path("data/clima.sqlite"),
                   help="Caminho para o banco")
    p.add_argument("--construir-graficos", action="store_true",
                   help="Se definido, gera os gráficos em 'reports/'.")
    
    return p.parse_args()

def main() -> None:
    #lendo os argumentos do terminal
    args = analisar_argumentos()
    cidades = [cidade.strip() for cidade in args.cidades.split(",") if cidade.strip()]
    data_final = dt.date.today()
    data_inicial = data_final - dt.timedelta(days=max(args.dias - 1, 0))

    print(f"Janela de tempo: {data_inicial.isoformat()} -> {data_final.isoformat()}")
    print(f"Cidades: {cidades}")

    inicializar_banco(args.banco_path)

    for cidade in cidades:
        try:
            geo = geocode_cidade(cidade)
            print(f"{cidade}: {geo['latitude']:}, {geo['longitude']:} (tz={geo['timezone']})")

            #criando um dataframe com os valores referentes as informações das cidades
            dados = buscar_clima_horario(
                geo["latitude"], geo["longitude"], data_inicial, data_final, timezone=geo["timezone"]
            )

            #gravando os dados do dataframe no banco de dados
            linhas = operacoes_por_horas(args.banco_path, geo["cidade"], geo["latitude"], geo["longitude"], dados)
            print(f"{cidade}: {linhas} linhas gravadas no banco.")

            if args.construir_graficos:
                d = lendo_cidade(args.banco_path, geo["cidade"])
                if not d.empty:
                    p1 = plotando_temperatura(d, geo["cidade"], "reports")
                    p2 = plotando_temperatura_diaria(d, geo["cidade"], "reports")
                    print(f"Gráficos gerados: {p1}, {p2}")
                else:
                    print(f"Sem dados para plotar em {cidade}.")
        except ApiError as e:
            print(f"Erro, {cidade}: {e}")
        except Exception as e:
            print(f"Erro, {cidade}: {type(e).__name__}: {e}")
    
    print("Pipeline concluído.")

if __name__ == "__main__":
    main()


