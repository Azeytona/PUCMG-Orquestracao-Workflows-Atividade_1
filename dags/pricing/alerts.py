import logging

log = logging.getLogger("alertas.pricing")


def _emitir(nivel: str, context: dict, detalhe: str = "") -> None:
    ti = context["task_instance"]
    # Simulação de alerta. Substituir por Slack, e-mail ou PagerDuty em produção.
    msg = "[ALERTA %s] dag=%s task=%s run=%s %s"
    args = (nivel, ti.dag_id, ti.task_id, context.get("run_id"), detalhe)
    if nivel == "FALHA":
        log.error(msg, *args)
    else:
        log.info(msg, *args)


def alerta_falha(context):
    _emitir("FALHA", context, f"erro={context.get('exception')}")


def alerta_retry(context):
    _emitir("RETRY", context, f"tentativa={context['task_instance'].try_number}")


def alerta_sucesso(context):
    _emitir("SUCESSO", context)