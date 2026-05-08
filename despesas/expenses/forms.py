from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Despesa, Categoria


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

    class Meta:
        model = Despesa
        fields = ["categoria", "valor", "data", "descricao"]
        widgets = {
            "valor": forms.NumberInput(attrs={"class": "form-control"}),
            "data": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "descricao": forms.Textarea(attrs={"class": "form-control"}),
        }
        labels = {
            "categoria": "Categoria",
            "valor": "Valor",
            "data": "Data",
            "descricao": "Descrição",
        }
        help_texts = {
            "categoria": "Selecione uma categoria",
            "valor": "Digite o valor da despesa",
            "data": "Digite a data da despesa",
            "descricao": "Digite uma descrição da despesa",
        }
        error_messages = {
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

        self.fields["valor"].widget.attrs["class"] = "form-control"
        self.fields["data"].widget.attrs["class"] = "form-control"
        self.fields["descricao"].widget.attrs["class"] = "form-control"

        self.fields["categoria"].widget.attrs[
            "placeholder"
        ] = "Selecione ou escreva uma categoria"
        self.fields["valor"].widget.attrs["placeholder"] = "Digite o valor da despesa"
        self.fields["data"].widget.attrs["placeholder"] = "Digite a data da despesa"
        self.fields["descricao"].widget.attrs[
            "placeholder"
        ] = "Digite uma descrição da despesa"

        self.fields["categoria"].help_text = "Selecione ou escreva uma categoria"
        self.fields["valor"].help_text = "Digite o valor da despesa"
        self.fields["data"].help_text = "Digite a data da despesa"
        self.fields["descricao"].help_text = "Digite uma descrição da despesa"

        self.fields["valor"].error_messages = {"required": "O valor é obrigatório"}
        self.fields["data"].error_messages = {"required": "A data é obrigatória"}
        self.fields["descricao"].error_messages = {
            "required": "A descrição é obrigatória"
        }

        self.fields["categoria"].label = "Categoria"
        self.fields["valor"].label = "Valor"
        self.fields["data"].label = "Data"
        self.fields["descricao"].label = "Descrição"

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
    username = forms.CharField(label="Utilizador")

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("Utilizador não encontrado")
