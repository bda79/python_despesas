from calendar import monthrange
from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from django.db.models import Avg, Count, FloatField, Sum
from django.db.models.functions import Cast
from django.utils import timezone

from ..models import Despesa


def periodo_mes(ano, mes):
    data_inicio = datetime(ano, mes, 1).date()
    _, ultimo_dia = monthrange(ano, mes)
    data_fim = datetime(ano, mes, ultimo_dia).date()
    return data_inicio, data_fim


def despesas_periodo(despesas_base, inicio, fim):
    return despesas_base.filter(tipo=Despesa.SAIDA, data__range=(inicio, fim))


def obter_contexto_dashboard(despesas_base, ano=None, mes=None):
    hoje = timezone.now()

    if isinstance(ano, (datetime, date)):
        hoje = ano
        ano_atual = hoje.year
        mes_atual = hoje.month
    else:
        ano_atual = ano or hoje.year
        mes_atual = mes or hoje.month

    data_inicio_atual, data_fim_atual = periodo_mes(ano_atual, mes_atual)
    despesas_mes_atual = despesas_periodo(
        despesas_base, data_inicio_atual, data_fim_atual
    )

    total_mes_atual = despesas_mes_atual.aggregate(Sum("valor"))["valor__sum"] or 0

    por_categoria = (
        despesas_mes_atual.values("categoria__nome")
        .annotate(
            total=Cast(Sum("valor"), FloatField()),
            numero_despesas=Count("id"),
            percentual=Cast(
                (
                    Sum("valor") * 100.0 / float(total_mes_atual)
                    if total_mes_atual > 0
                    else 0
                ),
                FloatField(),
            ),
        )
        .order_by("-total")
    )

    if mes_atual == 1:
        mes_anterior = 12
        ano_anterior = ano_atual - 1
    else:
        mes_anterior = mes_atual - 1
        ano_anterior = ano_atual

    # mês anterior
    if mes_atual == 1:
        mes_anterior_nav = 12
        ano_anterior_nav = ano_atual - 1
    else:
        mes_anterior_nav = mes_atual - 1
        ano_anterior_nav = ano_atual

    # mês seguinte
    if mes_atual == 12:
        mes_seguinte_nav = 1
        ano_seguinte_nav = ano_atual + 1
    else:
        mes_seguinte_nav = mes_atual + 1
        ano_seguinte_nav = ano_atual

    data_inicio_anterior, data_fim_anterior = periodo_mes(ano_anterior, mes_anterior)
    despesas_mes_anterior = despesas_periodo(
        despesas_base, data_inicio_anterior, data_fim_anterior
    )

    total_mes_anterior = (
        despesas_mes_anterior.aggregate(Sum("valor"))["valor__sum"] or 0
    )

    if total_mes_anterior > 0:
        variacao_percentual = (
            (float(total_mes_atual) - float(total_mes_anterior))
            / float(total_mes_anterior)
        ) * 100
    else:
        variacao_percentual = 0 if total_mes_atual == 0 else 100

    despesas_top = despesas_mes_atual  # despesas_base.filter(tipo=Despesa.SAIDA)

    top_categorias = (
        despesas_top.values("categoria__nome")
        .annotate(total=Cast(Sum("valor"), FloatField()), count=Count("id"))
        .order_by("-total")[:5]
    )

    data_inicio_3m = (hoje - relativedelta(months=3)).date()
    data_fim_3m = hoje.date()
    despesas_3m = despesas_base.filter(
        tipo=Despesa.SAIDA,
        data__range=(data_inicio_3m, data_fim_3m),
    )

    categoria_mais_cara = (
        despesas_3m.values("categoria__nome")
        .annotate(total=Cast(Sum("valor"), FloatField()))
        .order_by("-total")
        .first()
    )

    ticket_medio = despesas_mes_atual.aggregate(Avg("valor"))["valor__avg"] or 0

    dia_maior_gasto = (
        despesas_mes_atual.values("data")
        .annotate(total=Cast(Sum("valor"), FloatField()))
        .order_by("-total")
        .first()
    )

    evolucao = []
    for i in range(2, -1, -1):
        if mes_atual - i < 1:
            mes = 12 + (mes_atual - i)
            ano = ano_atual - 1
        else:
            mes = mes_atual - i
            ano = ano_atual

        data_inicio, data_fim = periodo_mes(ano, mes)
        despesas_mes = despesas_periodo(despesas_base, data_inicio, data_fim)

        total_mes = despesas_mes.aggregate(Sum("valor"))["valor__sum"] or 0
        meses = [
            "Jan",
            "Fev",
            "Mar",
            "Abr",
            "Mai",
            "Jun",
            "Jul",
            "Ago",
            "Set",
            "Out",
            "Nov",
            "Dez",
        ]
        evolucao.append(
            {
                "mes": f"{meses[mes - 1]} {ano}",
                "mes_numero": mes,
                "ano": ano,
                "total": float(total_mes),
            }
        )

    total_historico = (
        despesas_base.filter(tipo=Despesa.SAIDA).aggregate(total=Sum("valor"))
    )["total"] or 0

    MESES = [
        "",
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ]

    return {
        "total_mes_atual": total_mes_atual,
        "total_gasto_mes": total_mes_atual,  # usado no cartão
        "total_historico": total_historico,
        "por_categoria": por_categoria,
        "ticket_medio": float(ticket_medio),
        "total_anterior": total_mes_anterior,
        "variacao_percentual": round(variacao_percentual, 2),
        "mes_anterior": mes_anterior,
        "ano_anterior": ano_anterior,
        "top_categorias": top_categorias,
        "categoria_mais_cara": categoria_mais_cara,
        "dia_maior_gasto": dia_maior_gasto,
        "evolucao": evolucao,
        "mes_atual": mes_atual,
        "ano_atual": ano_atual,
        "mes_anterior_nav": mes_anterior_nav,
        "ano_anterior_nav": ano_anterior_nav,
        "mes_seguinte_nav": mes_seguinte_nav,
        "ano_seguinte_nav": ano_seguinte_nav,
        "nome_mes": MESES[mes_atual],
    }
