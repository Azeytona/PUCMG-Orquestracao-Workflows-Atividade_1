import logging

import requests

log = logging.getLogger(__name__)

API_URL = "https://fakestoreapi.com/products"


def buscar_produtos(timeout: int = 15) -> list[dict]:
    try:
        resp = requests.get(API_URL, timeout=timeout)
        resp.raise_for_status()
        produtos = resp.json()
    except (requests.RequestException, ValueError) as exc:
        log.warning("Falha ao consultar %s: %s", API_URL, exc)
        raise  # re-levanta para o Airflow acionar o retry

    if not produtos:
        raise ValueError("API retornou lista vazia")
    return produtos