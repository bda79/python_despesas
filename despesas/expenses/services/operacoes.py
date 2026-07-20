from django.core.cache import cache
from django.shortcuts import redirect
from django.utils import timezone


def _obter_contexto_dashboard(despesas_base, ano, mes):
    from .dashboard import obter_contexto_dashboard

    return obter_contexto_dashboard(despesas_base, ano, mes)


def invalidar_cache_dashboard(user):
    cache.delete(f"dashboard-{user.id}")


def obter_parametros_mes_ano(request, hoje=None):
    hoje = hoje or timezone.now()

    mes = request.GET.get("mes")
    ano = request.GET.get("ano")

    try:
        mes = int(str(mes).replace(".", "")) if mes else hoje.month
    except ValueError:
        mes = hoje.month

    try:
        ano = int(str(ano).replace(".", "")) if ano else hoje.year
    except ValueError:
        ano = hoje.year

    return mes, ano


def registar_despesa(request, form):
    if form.is_valid():
        despesa = form.save(commit=False)
        despesa.user = request.user
        despesa.save()
        invalidar_cache_dashboard(request.user)
        return True

    return False


def atualizar_despesa(request, form):
    if form.is_valid():
        form.save()
        invalidar_cache_dashboard(request.user)
        return True

    return False


def remover_despesa(request, despesa):
    despesa.delete()
    invalidar_cache_dashboard(request.user)


def redirecionar_se_partilha_invalida(request, redirect_name, tem_partilha):
    if request.GET.get("shared") == "1" and not tem_partilha:
        return redirect(redirect_name)
    return None


def obter_contexto_dashboard_view(
    request, tem_partilha, ver_conjunto, despesas_base, mes, ano, cache_timeout=300
):
    cache_key = f"dashboard-{request.user.id}-{ano}-{mes}-shared-{int(ver_conjunto)}"
    contexto_dashboard = cache.get(cache_key)

    if contexto_dashboard is None:
        contexto_dashboard = _obter_contexto_dashboard(
            despesas_base,
            ano,
            mes,
        )
        cache.set(cache_key, contexto_dashboard, cache_timeout)
    else:
        contexto_dashboard = dict(contexto_dashboard)

    contexto_dashboard.update(
        {
            "tem_partilha": tem_partilha,
            "ver_conjunto": ver_conjunto,
        }
    )
    return contexto_dashboard
