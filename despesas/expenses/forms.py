from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from .models import Despesa, Categoria


class DecimalPTField(forms.DecimalField):
    def to_python(self, value):
        if value in self.empty_values:
            return None

        if isinstance(value, Decimal):
            return value

        texto = str(value).strip().replace(" ", "")
        if not texto:
            return None

        for simbolo in ["€", "$", "R$", "£"]:
            texto = texto.replace(simbolo, "")

        if "," in texto and "." in texto:
            if texto.rfind(",") > texto.rfind("."):
                texto = texto.replace(".", "").replace(",", ".")
            else:
                texto = texto.replace(",", "")
        elif "," in texto:
            texto = texto.replace(",", ".")

        try:
            return Decimal(texto)
        except InvalidOperation:
            raise ValidationError(self.error_messages["invalid"], code="invalid")


class DespesaForm(forms.ModelForm):
    categoria = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "list": "categorias-list",
                "placeholder": "Selecione ou escreva uma categoria",
                "autocomplete": "off",
            }
        ),
        label="Categoria",
        help_text="Selecione ou escreva uma categoria",
        error_messages={"required": "A categoria é obrigatória"},
    )

    valor = DecimalPTField(
        required=True,
        label="Valor",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "inputmode": "decimal",
                "placeholder": "Digite o valor do movimento",
            }
        ),
        error_messages={
            "required": "O valor é obrigatório",
            "invalid": "Introduza um valor válido",
        },
    )

    class Meta:
        model = Despesa
        fields = ["tipo", "categoria", "valor", "data", "descricao"]
        widgets = {
            "tipo": forms.Select(attrs={"class": "form-control"}),
            "data": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "descricao": forms.Textarea(attrs={"class": "form-control"}),
        }
        labels = {
            "tipo": "Tipo",
            "categoria": "Categoria",
            "valor": "Valor",
            "data": "Data",
            "descricao": "Descrição",
        }

        error_messages = {
            "tipo": {"required": "O tipo de despesa é obrigatório"},
            "categoria": {"required": "A categoria é obrigatória"},
            "valor": {"required": "O valor é obrigatório"},
            "data": {"required": "A data é obrigatória"},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.categoria:
            categoria_nome = self.instance.categoria.nome
            self.initial["categoria"] = categoria_nome
            self.fields["categoria"].initial = categoria_nome

        self.fields["tipo"].widget.attrs["class"] = "form-control"
        self.fields["valor"].widget.attrs["class"] = "form-control"
        self.fields["data"].widget.attrs["class"] = "form-control"
        self.fields["descricao"].widget.attrs["class"] = "form-control"

        self.fields["tipo"].widget.attrs[
            "placeholder"
        ] = "Selecione o tipo de movimento"
        self.fields["categoria"].widget.attrs[
            "placeholder"
        ] = "Selecione ou escreva uma categoria"
        self.fields["valor"].widget.attrs["placeholder"] = "Digite o valor do movimento"
        self.fields["data"].widget.attrs["placeholder"] = "Digite a data do movimento"
        self.fields["descricao"].widget.attrs[
            "placeholder"
        ] = "Digite uma descrição do movimento"

        self.fields["valor"].error_messages = {"required": "O valor é obrigatório"}
        self.fields["data"].error_messages = {"required": "A data é obrigatória"}
        self.fields["descricao"].error_messages = {
            "required": "A descrição é obrigatória"
        }

        self.fields["tipo"].label = "Tipo"
        self.fields["categoria"].label = "Categoria"
        self.fields["valor"].label = "Valor"
        self.fields["data"].label = "Data"
        self.fields["descricao"].label = "Descrição"

        self.fields["tipo"].required = True
        self.fields["categoria"].required = True
        self.fields["valor"].required = True
        self.fields["data"].required = True
        self.fields["descricao"].required = True

    def clean_categoria(self):
        categoria_nome = self.cleaned_data["categoria"].strip()
        if not categoria_nome:
            raise forms.ValidationError("A categoria é obrigatória")

        categoria, _ = Categoria.objects.get_or_create(
            nome__iexact=categoria_nome,
            defaults={"nome": categoria_nome},
        )
        return categoria


class RegisterForm(UserCreationForm):

    email = forms.EmailField(required=True)

    class Meta:
        model = User

        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )


class CompartilharForm(forms.Form):

    identificador = forms.CharField(
        label="Email ou Username",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite email ou username",
            }
        ),
    )


class CustomSetPasswordForm(SetPasswordForm):

    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1")

        # Impede reutilizar a password atual
        if check_password(password, self.user.password):
            raise ValidationError(
                "A nova password não pode ser igual à password anterior."
            )

        return password
