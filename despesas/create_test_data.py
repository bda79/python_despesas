from django.contrib.auth import get_user_model
from expenses.models import Categoria, Despesa
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()
user = User.objects.get(username="test")

# Create some categories
categorias = ["Caixa IN", "Conta Conjunto", "Farmácia", "Forno Real", "Glovo Portugal"]
for cat_nome in categorias:
    Categoria.objects.get_or_create(nome=cat_nome)

# Create test expenses
hoje = timezone.now()
despesas_data = [
    ("Caixa IN", 100.00, 2),
    ("Conta Conjunto", 250.50, 5),
    ("Farmácia", 45.80, 8),
    ("Forno Real", 85.30, 12),
    ("Glovo Portugal", 120.00, 15),
    ("Caixa IN", 75.50, 18),
    ("Farmácia", 30.00, 22),
]

for cat_nome, valor, dias_atras in despesas_data:
    cat = Categoria.objects.get(nome=cat_nome)
    data = (hoje - timedelta(days=dias_atras)).date()
    Despesa.objects.get_or_create(
        user=user,
        categoria=cat,
        tipo="saida",
        valor=valor,
        data=data,
        descricao=f"Despesa de teste - {cat_nome}",
    )

print("Despesas criadas com sucesso!")
