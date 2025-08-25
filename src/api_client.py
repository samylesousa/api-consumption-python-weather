from __future__ import annotations

import datetime as dt
from typing import Dict, Any

import pandas as pd
import requests

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

class ApiError(RuntimeError):
    pass

def geocode_cidade(cidade: str, idioma: str = "pt", timeout: int = 20) -> Dict[str, Any]:
    """Função que recebe parâmetros referentes a uma cidade e retorna um dicionário com 
    os valores de longitude e latitude."""

    parametros = {
        "name": cidade,
        "count": 1,
        "language": idioma,
        "format": "json",
    }

    requisicao = requests.get(GEO_URL, params=parametros, timeout=timeout)
    requisicao.raise_for_status()
    dados = requisicao.json()
    resultados = dados.get("results") or []
    if not resultados:
        raise ApiError("Não foram encontradas coordenadas para a cidade informada")

    primeiro_resultado = resultados[0]

    return {
        "cidade": primeiro_resultado["name"],
        "latitude": primeiro_resultado["latitude"],
        "longitude": primeiro_resultado["longitude"],
        "codigo_pais": primeiro_resultado.get("country_code"),
        "timezone": primeiro_resultado.get("timezone", "auto"),
    }    

def buscar_clima_horario(
        latitude: float,
        longitude: float,
        data_inicio: dt.date,
        data_final: dt.date,
        timezone: str = "auto",
        timeout: int = 60,
        ) -> pd.DataFrame:
    
    """Baixa dados horários de tempetura, umidade e velocidade do vento.
    Retorna um DataFrame com o timestamp, temperatura, umidade e velocidade do vento.
    """

    horas_valores = "temperature_2m,relativehumidity_2m,windspeed_10m"
    parametros = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": data_inicio,
        "end_date": data_final,
        "timezone": timezone,
        "timeout": timeout,
        "hourly": horas_valores,
    }

    requisicao = requests.get(FORECAST_URL, params=parametros, timeout=timeout)
    requisicao.raise_for_status()
    dados = requisicao.json()

    hora_em_hora = dados.get("hourly") or {}

    # esse if é para verificar se todos os atributos necessários foram retornados pela API
    if not all(k in hora_em_hora for k in ["time", "temperature_2m", "relativehumidity_2m", "windspeed_10m"]):
        raise ApiError("Resposta inesperada da API")
    
    dadosDataFrame = pd.DataFrame({
        "timestamp": hora_em_hora["time"],
        "temperatura": hora_em_hora["temperature_2m"],
        "umidade": hora_em_hora["relativehumidity_2m"],
        "velocidade_vento": hora_em_hora["windspeed_10m"]
    })

    # modificando os dados de data para facilitar a análise
    dadosDataFrame["timestamp"] = pd.to_datetime(dadosDataFrame["timestamp"], utc=False)
    return dadosDataFrame
