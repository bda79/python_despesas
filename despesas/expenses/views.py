from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Sum, FloatField, Q
from django.db.models.functions import Cast
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

    total = despesas.aggregate(Sum("valor"))["valor__sum"] or 0

    return render(
        request,
        "lista.html",
        {
            "despesas": despesas,
            "total": total,
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
def dashboard(request):
    despesas = Despesa.objects.filter(user=request.user)

    total = despesas.aggregate(Sum("valor"))["valor__sum"] or 0

    # por_categoria = despesas.values("categoria__nome").annotate(total=Sum("valor"))
    por_categoria = despesas.values("categoria__nome").annotate(
        total=Cast(Sum("valor"), FloatField())
    )

    return render(
        request, "dashboard.html", {"total": total, "por_categoria": por_categoria}
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
    return JsonResponse({"status": "alive"})
