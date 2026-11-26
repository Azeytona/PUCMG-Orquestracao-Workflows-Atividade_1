from pricing.metrics import calcular_metricas_categoria, listar_categorias


def test_listar_categorias_ordenadas_e_unicas():
    produtos = [{"category": "b"}, {"category": "a"}, {"category": "b"}]
    assert listar_categorias(produtos) == ["a", "b"]


def test_metricas_por_categoria():
    produtos = [
        {"category": "a", "price": 10},
        {"category": "a", "price": 20},
        {"category": "b", "price": 5},
    ]
    m = calcular_metricas_categoria(produtos, "a")
    assert m["avg_price"] == 15
    assert m["min_price"] == 10
    assert m["max_price"] == 20
    assert m["product_count"] == 2