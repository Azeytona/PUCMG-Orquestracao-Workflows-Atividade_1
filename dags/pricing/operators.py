from airflow.exceptions import AirflowException
from airflow.models import BaseOperator


class ValidarProdutosOperator(BaseOperator):
    """Valida o schema dos produtos antes do processamento."""

    REQUIRED_FIELDS = {"id": int, "category": str, "price": (int, float)}

    def __init__(self, source_task_id: str, **kwargs):
        super().__init__(**kwargs)
        self.source_task_id = source_task_id

    def execute(self, context):
        produtos = context["ti"].xcom_pull(task_ids=self.source_task_id)
        erros = []

        for i, p in enumerate(produtos):
            for campo, tipo in self.REQUIRED_FIELDS.items():
                valor = p.get(campo)
                if not isinstance(valor, tipo) or isinstance(valor, bool):
                    erros.append(f"produto[{i}].{campo} inválido: {valor!r}")
            if isinstance(p.get("price"), (int, float)) and p["price"] < 0:
                erros.append(f"produto[{i}].price negativo: {p['price']}")

        if erros:
            raise AirflowException(f"{len(erros)} erro(s) de schema: {erros[:5]}")

        self.log.info("%d produtos validados", len(produtos))
        return produtos  # XCom: passa a lista adiante