from decimal import Decimal

from django.db.models import Case, DecimalField, Sum, Value, When

from ..models import Despesa


def calcular_totais(queryset):
    totais = queryset.aggregate(
        entradas=Sum(
            Case(
                When(tipo=Despesa.ENTRADA, then="valor"),
                default=Value(0),
                output_field=DecimalField(),
            )
        ),
        saidas=Sum(
            Case(
                When(tipo=Despesa.SAIDA, then="valor"),
                default=Value(0),
                output_field=DecimalField(),
            )
        ),
    )

    entradas = totais["entradas"] or Decimal("0.00")
    saidas = totais["saidas"] or Decimal("0.00")
    saldo = entradas - saidas
    return entradas, saidas, saldo


def obter_resumo_mensal(despesas_base, mes, ano):
    movimentos = despesas_base.filter(data__month=mes, data__year=ano)
    entradas, saidas, saldo = calcular_totais(movimentos)
    return movimentos, entradas, saidas, saldo


def obter_resumo_anual(despesas_base, ano):
    movimentos = despesas_base.filter(data__year=ano).order_by("-data")
    entradas, saidas, saldo = calcular_totais(movimentos)
    return movimentos, entradas, saidas, saldo
