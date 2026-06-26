from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Sum, FloatField, Q, Avg, Count
from django.db.models.functions import Cast
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange
from .forms import DespesaForm, RegisterForm, CompartilharForm
from .models import Despesa, Categoria, Compartilhamento


def login_view(request):
    if request.user.is_authenticated:
        return redirect("lista")

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get("next", "lista")
                return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    # return redirect("login")
    return JsonResponse({"status": "logged_out"})


def register_view(request):

    if request.user.is_authenticated:
        return redirect("lista")

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            messages.success(request, "Conta criada com sucesso.")

            return redirect("lista")

        else:

            messages.error(request, "Por favor corrija os erros.")

    else:

        form = RegisterForm()

    return render(request, "register.html", {"form": form})


@login_required
def lista_despesas(request):

    compartilhamento = Compartilhamento.objects.filter(shared_user=request.user).first()

    tem_partilha = compartilhamento is not None

    ver_conjunto = request.GET.get("shared") == "1" and tem_partilha

    # impedir acesso manual
    if request.GET.get("shared") == "1" and not tem_partilha:
        return redirect("lista")

    if ver_conjunto:

        despesas = Despesa.objects.filter(
            Q(user=request.user) | Q(user=compartilhamento.owner)
        )

    else:

        despesas = Despesa.objects.filter(user=request.user)

    total_entradas = (
        despesas.filter(tipo="entrada").aggregate(Sum("valor"))["valor__sum"] or 0
    )

    total_saidas = (
        despesas.filter(tipo="saida").aggregate(Sum("valor"))["valor__sum"] or 0
    )

    saldo = total_entradas - total_saidas

    return render(
        request,
        "lista.html",
        {
            "despesas": despesas,
            "total_entradas": total_entradas,
            "total_saidas": total_saidas,
            "saldo": saldo,
            "tem_partilha": tem_partilha,
            "ver_conjunto": ver_conjunto,
        },
    )


@login_required
def nova_despesa(request):
    form = DespesaForm(request.POST or None)
    categorias = Categoria.objects.order_by("nome")

    if form.is_valid():
        despesa = form.save(commit=False)
        despesa.user = request.user
        despesa.save()
        messages.success(request, "Despesa registada com sucesso.")
        return redirect("lista")

    elif request.method == "POST":
        messages.error(request, "Por favor corrija os erros no formulário.")

    return render(
        request,
        "nova_despesa.html",
        {"form": form, "categorias": categorias, "is_edit": False},
    )


@login_required
def editar_despesa(request, id):
    despesa = get_object_or_404(Despesa, id=id, user=request.user)
    form = DespesaForm(request.POST or None, instance=despesa)
    categorias = Categoria.objects.order_by("nome")

    if form.is_valid():
        form.save()
        messages.success(request, "Despesa atualizada com sucesso.")
        return redirect("lista")

    elif request.method == "POST":
        messages.error(request, "Por favor corrija os erros no formulário.")

    return render(
        request,
        "nova_despesa.html",
        {"form": form, "is_edit": True, "categorias": categorias},
    )


@login_required
def apagar_despesa(request, id):
    despesa = get_object_or_404(Despesa, id=id, user=request.user)

    if request.method == "POST":
        despesa.delete()
        messages.success(request, "Despesa apagada com sucesso.")
        return redirect("lista")

    return render(request, "confirmar_apagar.html", {"despesa": despesa})


@login_required
def resumo_mensal(request):

    hoje = timezone.now()

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

    compartilhamento = Compartilhamento.objects.filter(shared_user=request.user).first()

    tem_partilha = compartilhamento is not None

    ver_conjunto = request.GET.get("shared") == "1" and tem_partilha

    # impedir acesso manual
    if request.GET.get("shared") == "1" and not tem_partilha:
        return redirect("resumo_mensal")

    if ver_conjunto:

        movimentos = Despesa.objects.filter(
            Q(user=request.user) | Q(user=compartilhamento.owner),
            data__month=mes,
            data__year=ano,
        )

    else:

        movimentos = Despesa.objects.filter(
            user=request.user,
            data__month=mes,
            data__year=ano,
        )

    entradas = (
        movimentos.filter(tipo="entrada").aggregate(Sum("valor"))["valor__sum"] or 0
    )

    saidas = movimentos.filter(tipo="saida").aggregate(Sum("valor"))["valor__sum"] or 0

    saldo = entradas - saidas

    return render(
        request,
        "resumo_mensal.html",
        {
            "movimentos": movimentos,
            "entradas": entradas,
            "saidas": saidas,
            "saldo": saldo,
            "mes": mes,
            "ano": ano,
            "tem_partilha": tem_partilha,
            "ver_conjunto": ver_conjunto,
        },
    )


@login_required
def resumo_anual(request):

    hoje = timezone.now()

    ano = request.GET.get("ano")

    try:
        ano = int(str(ano).replace(".", "")) if ano else hoje.year
    except ValueError:
        ano = hoje.year

    compartilhamento = Compartilhamento.objects.filter(shared_user=request.user).first()

    tem_partilha = compartilhamento is not None

    ver_conjunto = request.GET.get("shared") == "1" and tem_partilha

    if request.GET.get("shared") == "1" and not tem_partilha:
        return redirect("resumo_anual")

    if ver_conjunto:

        movimentos = Despesa.objects.filter(
            Q(user=request.user) | Q(user=compartilhamento.owner),
            data__year=ano,
        ).order_by("-data")

    else:

        movimentos = Despesa.objects.filter(
            user=request.user,
            data__year=ano,
        ).order_by("-data")

    entradas = (
        movimentos.filter(tipo="entrada").aggregate(total=Sum("valor"))["total"] or 0
    )

    saidas = movimentos.filter(tipo="saida").aggregate(total=Sum("valor"))["total"] or 0

    saldo = entradas - saidas

    return render(
        request,
        "resumo_anual.html",
        {
            "movimentos": movimentos,
            "entradas": entradas,
            "saidas": saidas,
            "saldo": saldo,
            "ano": ano,
            "tem_partilha": tem_partilha,
            "ver_conjunto": ver_conjunto,
        },
    )


@login_required
def dashboard(request):

    compartilhamento = Compartilhamento.objects.filter(shared_user=request.user).first()
    tem_partilha = compartilhamento is not None
    ver_conjunto = request.GET.get("shared") == "1" and tem_partilha

    # impedir acesso manual
    if request.GET.get("shared") == "1" and not tem_partilha:
        return redirect("dashboard")

    # ========== PERÍODO ATUAL (MÊS ATUAL) ==========
    hoje = timezone.now()
    mes_atual = hoje.month
    ano_atual = hoje.year

    _, ultimo_dia = monthrange(ano_atual, mes_atual)
    data_inicio_atual = datetime(ano_atual, mes_atual, 1).date()
    data_fim_atual = datetime(ano_atual, mes_atual, ultimo_dia).date()

    if ver_conjunto:
        despesas_atual = Despesa.objects.filter(
            Q(user=request.user) | Q(user=compartilhamento.owner),
            tipo="saida",
            data__gte=data_inicio_atual,
            data__lte=data_fim_atual,
        )
    else:
        despesas_atual = Despesa.objects.filter(
            user=request.user,
            tipo="saida",
            data__gte=data_inicio_atual,
            data__lte=data_fim_atual,
        )

    # Total período atual
    total_atual = despesas_atual.aggregate(Sum("valor"))["valor__sum"] or 0

    # Por categoria - período atual
    por_categoria = (
        despesas_atual.values("categoria__nome")
        .annotate(
            total=Cast(Sum("valor"), FloatField()),
            percentual=Cast(
                Sum("valor") * 100.0 / float(total_atual) if total_atual > 0 else 0,
                FloatField(),
            ),
        )
        .order_by("-total")
    )

    # ========== PERÍODO ANTERIOR (MÊS PASSADO) ==========
    # Calcular mês e ano anterior
    if mes_atual == 1:
        mes_anterior = 12
        ano_anterior = ano_atual - 1
    else:
        mes_anterior = mes_atual - 1
        ano_anterior = ano_atual

    _, ultimo_dia_anterior = monthrange(ano_anterior, mes_anterior)
    data_inicio_anterior = datetime(ano_anterior, mes_anterior, 1).date()
    data_fim_anterior = datetime(ano_anterior, mes_anterior, ultimo_dia_anterior).date()

    if ver_conjunto:
        despesas_anterior = Despesa.objects.filter(
            Q(user=request.user) | Q(user=compartilhamento.owner),
            tipo="saida",
            data__gte=data_inicio_anterior,
            data__lte=data_fim_anterior,
        )
    else:
        despesas_anterior = Despesa.objects.filter(
            user=request.user,
            tipo="saida",
            data__gte=data_inicio_anterior,
            data__lte=data_fim_anterior,
        )

    total_anterior = despesas_anterior.aggregate(Sum("valor"))["valor__sum"] or 0

    # Variação percentual
    if total_anterior > 0:
        variacao_percentual = (
            (float(total_atual) - float(total_anterior)) / float(total_anterior)
        ) * 100
    else:
        variacao_percentual = 0 if total_atual == 0 else 100

    # ========== TOP 5 CATEGORIAS ==========
    if ver_conjunto:
        despesas_top = Despesa.objects.filter(
            Q(user=request.user) | Q(user=compartilhamento.owner), tipo="saida"
        )
    else:
        despesas_top = Despesa.objects.filter(user=request.user, tipo="saida")

    top_categorias = (
        despesas_top.values("categoria__nome")
        .annotate(total=Cast(Sum("valor"), FloatField()), count=Count("id"))
        .order_by("-total")[:5]
    )

    # ========== KPIs ==========
    # Categoria mais cara (geral - últimas 3 meses)
    tres_meses_atras = hoje - timedelta(days=90)
    if ver_conjunto:
        despesas_3m = Despesa.objects.filter(
            Q(user=request.user) | Q(user=compartilhamento.owner),
            tipo="saida",
            data__gte=tres_meses_atras,
        )
    else:
        despesas_3m = Despesa.objects.filter(
            user=request.user, tipo="saida", data__gte=tres_meses_atras
        )

    categoria_mais_cara = (
        despesas_3m.values("categoria__nome")
        .annotate(total=Cast(Sum("valor"), FloatField()))
        .order_by("-total")
        .first()
    )

    # Ticket médio
    ticket_medio = despesas_atual.aggregate(Avg("valor"))["valor__avg"] or 0

    # Dia com maior gasto (período atual)
    dia_maior_gasto = (
        despesas_atual.values("data")
        .annotate(total=Cast(Sum("valor"), FloatField()))
        .order_by("-total")
        .first()
    )

    # ========== EVOLUÇÃO MENSAL (últimos 3 meses) ==========
    evolucao = []
    for i in range(2, -1, -1):  # últimos 3 meses (incluindo atual)
        if mes_atual - i < 1:
            mes = 12 + (mes_atual - i)
            ano = ano_atual - 1
        else:
            mes = mes_atual - i
            ano = ano_atual

        _, ultimo_dia_mes = monthrange(ano, mes)
        data_inicio = datetime(ano, mes, 1).date()
        data_fim = datetime(ano, mes, ultimo_dia_mes).date()

        if ver_conjunto:
            despesas_mes = Despesa.objects.filter(
                Q(user=request.user) | Q(user=compartilhamento.owner),
                tipo="saida",
                data__gte=data_inicio,
                data__lte=data_fim,
            )
        else:
            despesas_mes = Despesa.objects.filter(
                user=request.user,
                tipo="saida",
                data__gte=data_inicio,
                data__lte=data_fim,
            )

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
                "mes": f"{meses[mes-1]} {ano}",
                "mes_numero": mes,
                "ano": ano,
                "total": float(total_mes),
            }
        )

    return render(
        request,
        "dashboard.html",
        {
            # Período atual
            "total": total_atual,
            "por_categoria": por_categoria,
            "ticket_medio": float(ticket_medio),
            # Período anterior e comparativa
            "total_anterior": total_anterior,
            "variacao_percentual": round(variacao_percentual, 2),
            "mes_anterior": mes_anterior,
            "ano_anterior": ano_anterior,
            # Top categorias
            "top_categorias": top_categorias,
            # KPIs
            "categoria_mais_cara": categoria_mais_cara,
            "dia_maior_gasto": dia_maior_gasto,
            # Evolução
            "evolucao": evolucao,
            # Compartilhamento
            "tem_partilha": tem_partilha,
            "ver_conjunto": ver_conjunto,
        },
    )


@login_required
def configuracoes(request):

    partilha_existente = Compartilhamento.objects.filter(owner=request.user).first()

    form = CompartilharForm()

    # REMOVER
    if request.method == "POST" and "remove_partilha" in request.POST:

        Compartilhamento.objects.filter(owner=request.user).delete()

        messages.success(request, "Partilha removida.")

        return redirect("configuracoes")

    # ADICIONAR
    if request.method == "POST" and "identificador" in request.POST:

        form = CompartilharForm(request.POST)

        if form.is_valid():

            identificador = form.cleaned_data["identificador"]

            user = User.objects.filter(
                Q(email=identificador) | Q(username=identificador)
            ).first()

            if not user:

                form.add_error("identificador", "Utilizador não encontrado.")

            elif user == request.user:

                form.add_error("identificador", "Não pode partilhar consigo mesmo.")

            elif partilha_existente:

                form.add_error("identificador", "Já existe uma partilha configurada.")

            else:

                Compartilhamento.objects.create(
                    owner=request.user,
                    shared_user=user,
                )

                messages.success(request, "Partilha criada com sucesso.")

                return redirect("configuracoes")
    return render(
        request,
        "configuracoes.html",
        {
            "form": form,
            "partilha_existente": partilha_existente,
        },
    )


@login_required
def keep_alive(request):
    request.session.modified = True
    return JsonResponse({"status": "alive"})


@login_required
def api_despesas(request):

    query = request.GET.get("q", "").strip()
    categoria = request.GET.get("categoria", "").strip()

    compartilhamento = Compartilhamento.objects.filter(shared_user=request.user).first()
    tem_partilha = compartilhamento is not None
    ver_conjunto = request.GET.get("shared") == "1" and tem_partilha

    if ver_conjunto:
        qs = Despesa.objects.filter(
            Q(user=request.user) | Q(user=compartilhamento.owner)
        )
    else:
        qs = Despesa.objects.filter(user=request.user)

    if query:
        qs = qs.filter(
            Q(descricao__icontains=query) | Q(categoria__nome__icontains=query)
        )

    if categoria:
        qs = qs.filter(categoria__nome__icontains=categoria)

    qs = qs.order_by("-data")[:200]

    data = list(
        qs.values(
            "id",
            "descricao",
            "valor",
            "tipo",
            "categoria__nome",
            "data",
            "user__username",
        )
    )

    return JsonResponse({"count": len(data), "results": data})


@login_required
def api_categorias(request):

    term = request.GET.get("q", "")

    categorias = Categoria.objects.filter(nome__icontains=term).values("nome")[:8]

    return JsonResponse(list(categorias), safe=False)
