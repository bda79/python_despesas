import uuid

from django.db import models
from django.contrib.auth.models import User


class DespesaQuerySet(models.QuerySet):
    def saidas(self):
        return self.filter(tipo=Despesa.SAIDA)

    def entradas(self):
        return self.filter(tipo=Despesa.ENTRADA)

    def do_utilizador(self, user):
        return self.filter(user=user)


class Categoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Despesa(models.Model):
    ENTRADA = "entrada"
    SAIDA = "saida"

    TIPO_COICES = [(SAIDA, "Saída"), (ENTRADA, "Entrada")]

    objects = DespesaQuerySet.as_manager()

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")

    tipo = models.CharField(max_length=10, choices=TIPO_COICES, verbose_name="Tipo")

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Categoria",
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    data = models.DateField(verbose_name="Data")
    descricao = models.TextField(blank=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Movimento"
        verbose_name_plural = "Movimentos"
        ordering = ["-data"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["data"]),
            models.Index(fields=["tipo"]),
            models.Index(fields=["categoria"]),
            models.Index(fields=["user", "data"]),
        ]

    def __str__(self):
        return f"{self.valor}€ - {self.categoria}"


class Compartilhamento(models.Model):

    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="compartilhamento",
    )

    shared_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recebe_acesso",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("owner", "shared_user")

    def __str__(self):
        return f"{self.shared_user} pode ver despesas de {self.owner}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_valid(self):
        from datetime import timedelta
        from django.utils import timezone

        return not self.used and self.created_at > timezone.now() - timedelta(
            minutes=30
        )
