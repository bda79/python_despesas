from django.db import models
from django.contrib.auth.models import User


class Categoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Despesa(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Categoria",
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    data = models.DateField(verbose_name="Data")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    """ shared_with = models.ManyToManyField(
        User, related_name="despesas_partilhadas", blank=True
    ) """

    class Meta:
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"
        ordering = ["-data"]

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


# Create your models here.
