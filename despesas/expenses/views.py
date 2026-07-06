from urllib.parse import quote

from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from calendar import monthrange
from .forms import DespesaForm, RegisterForm, CompartilharForm
from .models import Despesa, Categoria, Compartilhamento
from .services.operacoes import (
    atualizar_despesa,
    invalidar_cache_dashboard,
    obter_contexto_dashboard_view,
    obter_parametros_mes_ano,
    redirecionar_se_partilha_invalida,
    registar_despesa,
    remover_despesa,
)
from .services.partilha import obter_despesas, obter_estado_partilha
from .services.resumo import calcular_totais, obter_resumo_anual, obter_resumo_mensal


def periodo_mes(ano, mes):
    data_inicio = datetime(ano, mes, 1).date()
    _, ultimo_dia = monthrange(ano, mes)
    data_fim = datetime(ano, mes, ultimo_dia).date()
    return data_inicio, data_fim


def redirect_with_message(request, message, destination):
    messages.success(request, message)
    return redirect(destination)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("lista")

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
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

            return redirect_with_message(request, "Conta criada com sucesso.", "lista")

        else:

            messages.error(request, "Por favor corrija os erros.")

    else:

        form = RegisterForm()

    return render(request, "register.html", {"form": form})


@login_required
def lista_despesas(request):
    despesas, tem_partilha, ver_conjunto = obter_despesas(request)

    redirecao = redirecionar_se_partilha_invalida(request, "lista", tem_partilha)
    if redirecao is not None:
        return redirecao

    total_entradas, total_saidas, saldo = calcular_totais(despesas)

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

    if registar_despesa(request, form):
        return redirect_with_message(request, "Despesa registada com sucesso.", "lista")

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

    if atualizar_despesa(request, form):
        return redirect_with_message(
            request, "Despesa atualizada com sucesso.", "lista"
        )

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
        remover_despesa(request, despesa)
        return redirect_with_message(request, "Despesa apagada com sucesso.", "lista")

    return render(request, "confirmar_apagar.html", {"despesa": despesa})


@login_required
def resumo_mensal(request):
    hoje = timezone.now()
    mes, ano = obter_parametros_mes_ano(request, hoje)

    _, tem_partilha, ver_conjunto = obter_estado_partilha(request)

    redirecao = redirecionar_se_partilha_invalida(
        request, "resumo_mensal", tem_partilha
    )
    if redirecao is not None:
        return redirecao

    despesas_base, _, _ = obter_despesas(request)
    movimentos, entradas, saidas, saldo = obter_resumo_mensal(despesas_base, mes, ano)

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
    _, ano = obter_parametros_mes_ano(request, hoje)

    _, tem_partilha, ver_conjunto = obter_estado_partilha(request)

    redirecao = redirecionar_se_partilha_invalida(request, "resumo_anual", tem_partilha)
    if redirecao is not None:
        return redirecao

    despesas_base, _, _ = obter_despesas(request)
    movimentos, entradas, saidas, saldo = obter_resumo_anual(despesas_base, ano)

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
    _, tem_partilha, ver_conjunto = obter_estado_partilha(request)

    redirecao = redirecionar_se_partilha_invalida(request, "dashboard", tem_partilha)
    if redirecao is not None:
        return redirecao

    mes, ano = obter_parametros_mes_ano(request, timezone.now())

    despesas_base, _, _ = obter_despesas(request)
    contexto_dashboard = obter_contexto_dashboard_view(
        request,
        tem_partilha,
        ver_conjunto,
        despesas_base,
        mes,
        ano,
    )

    return render(request, "dashboard.html", contexto_dashboard)


@login_required
def gestao_categorias(request):
    query = request.GET.get("q", "").strip()
    categorias = Categoria.objects.order_by("nome")

    if query:
        categorias = categorias.filter(nome__icontains=query)

    if request.method == "POST":
        if "delete_categoria" in request.POST:
            categoria_id = request.POST.get("delete_categoria")
            categoria = get_object_or_404(Categoria, pk=categoria_id)

            if Despesa.objects.filter(categoria=categoria).exists():
                messages.error(
                    request,
                    "Esta categoria não pode ser removida porque tem despesas associadas.",
                )
            else:
                categoria.delete()
                messages.success(request, "Categoria removida com sucesso.")

            redirect_url = reverse("gestao_categorias")
            if query:
                redirect_url = f"{redirect_url}?q={quote(query)}"
            return redirect(redirect_url)

        categoria_id = request.POST.get("categoria_id")
        nome = request.POST.get("nome", "").strip()

        if categoria_id and nome:
            categoria = get_object_or_404(Categoria, pk=categoria_id)
            categoria.nome = nome
            categoria.save()
            messages.success(request, "Categoria atualizada com sucesso.")

            redirect_url = reverse("gestao_categorias")
            if query:
                redirect_url = f"{redirect_url}?q={quote(query)}"
            return redirect(redirect_url)

        messages.error(request, "O nome da categoria é obrigatório.")

    return render(
        request,
        "gestao_categorias.html",
        {"categorias": categorias, "query": query},
    )


@login_required
def configuracoes(request):

    partilha_existente = Compartilhamento.objects.filter(owner=request.user).first()

    form = CompartilharForm()

    # REMOVER
    if request.method == "POST" and "remove_partilha" in request.POST:

        Compartilhamento.objects.filter(owner=request.user).delete()
        invalidar_cache_dashboard(request.user)

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
                invalidar_cache_dashboard(request.user)

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

    _, tem_partilha, ver_conjunto = obter_estado_partilha(request)
    qs, _, _ = obter_despesas(request)

    if query:
        qs = qs.filter(
            Q(descricao__icontains=query) | Q(categoria__nome__icontains=query)
        )

    if categoria:
        qs = qs.filter(categoria__nome__icontains=categoria)

    qs = (
        qs.select_related("categoria", "user")
        .only(
            "descricao",
            "valor",
            "tipo",
            "data",
            "categoria__nome",
            "user__username",
        )
        .order_by("-data")[:200]
    )

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
