from __future__ import annotations


def listar_categorias(produtos: list[dict]) -> list[str]:
    """Categorias descobertas dos dados: novas categorias entram sem alterar código."""
    return sorted({p["category"] for p in produtos})


def calcular_metricas_categoria(produtos: list[dict], categoria: str) -> dict:
    precos = [float(p["price"]) for p in produtos if p["category"] == categoria]
    if not precos:
        raise ValueError(f"Categoria sem produtos: {categoria}")
    return {
        "category": categoria,
        "avg_price": round(sum(precos) / len(precos), 2),
        "min_price": round(min(precos), 2),
        "max_price": round(max(precos), 2),
        "product_count": len(precos),
    }