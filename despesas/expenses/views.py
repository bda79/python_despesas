from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from .forms import DespesaForm, RegisterForm
from .models import Despesa, Categoria


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
    despesas = Despesa.objects.filter(user=request.user)
    total = sum(d.valor for d in despesas)

    return render(request, "lista.html", {"despesas": despesas, "total": total})


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
def keep_alive(request):
    return JsonResponse({"status": "alive"})
