from decimal import Decimal

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from .forms import DespesaForm
from .models import Categoria, Compartilhamento, Despesa
from .services.dashboard import obter_contexto_dashboard
from .services.partilha import obter_despesas, obter_estado_partilha
from .services.resumo import calcular_totais, obter_resumo_anual, obter_resumo_mensal


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class HelpersRefactorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="user1", password="pass123")
        self.owner = User.objects.create_user(username="owner", password="pass123")
        self.categoria = Categoria.objects.create(nome="Alimentação")

        Compartilhamento.objects.create(owner=self.owner, shared_user=self.user)

        Despesa.objects.create(
            user=self.user,
            tipo=Despesa.SAIDA,
            categoria=self.categoria,
            valor="10.50",
            data="2024-01-01",
            descricao="Mercado",
        )
        Despesa.objects.create(
            user=self.owner,
            tipo=Despesa.ENTRADA,
            categoria=self.categoria,
            valor="20.00",
            data="2024-01-02",
            descricao="Salário",
        )

    def test_obter_estado_partilha_retorna_estado_de_partilha(self):
        request = self.factory.get("/?shared=1")
        request.user = self.user

        compartilhamento, tem_partilha, ver_conjunto = obter_estado_partilha(request)

        self.assertEqual(compartilhamento.owner, self.owner)
        self.assertTrue(tem_partilha)
        self.assertTrue(ver_conjunto)

    def test_obter_despesas_inclui_despesas_do_owner_quando_partilhado(self):
        request = self.factory.get("/?shared=1")
        request.user = self.user

        despesas, tem_partilha, ver_conjunto = obter_despesas(request)

        self.assertTrue(tem_partilha)
        self.assertTrue(ver_conjunto)
        self.assertEqual(despesas.count(), 2)

    def test_calcular_totais_retorna_entradas_saidas_e_saldo(self):
        despesas = Despesa.objects.filter(user=self.user)

        entradas, saidas, saldo = calcular_totais(despesas)

        self.assertEqual(entradas, Decimal("0.00"))
        self.assertEqual(saidas, Decimal("10.50"))
        self.assertEqual(saldo, Decimal("-10.50"))

    def test_obter_contexto_dashboard_retorna_metricas_basicas(self):
        despesas = Despesa.objects.filter(user=self.user)
        hoje = self.user.date_joined.replace(year=2024, month=1, day=1)

        contexto = obter_contexto_dashboard(despesas, hoje)

        self.assertEqual(contexto["total_mes_atual"], Decimal("10.50"))
        self.assertEqual(contexto["total_historico"], Decimal("10.50"))
        self.assertEqual(len(contexto["evolucao"]), 3)
        self.assertIn("por_categoria", contexto)

    def test_formulario_aceita_valor_em_formato_portugues(self):
        form = DespesaForm(
            data={
                "tipo": Despesa.SAIDA,
                "categoria": self.categoria.nome,
                "valor": "1.254,65",
                "data": "2024-01-03",
                "descricao": "Compras",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["valor"], Decimal("1254.65"))

    def test_queryset_personalizado_expõe_filtros_comuns(self):
        self.assertEqual(Despesa.objects.saidas().count(), 1)
        self.assertEqual(Despesa.objects.entradas().count(), 1)
        self.assertEqual(Despesa.objects.do_utilizador(self.user).count(), 1)

    def test_gestao_de_categorias_permita_editar_e_remover(self):
        self.client.force_login(self.user)

        categoria = Categoria.objects.create(nome="Alimentação")

        response = self.client.post(
            reverse("gestao_categorias"),
            {"categoria_id": categoria.id, "nome": "Alimentação Atualizada"},
            follow=True,
        )

        self.assertContains(response, "Categoria atualizada")
        categoria.refresh_from_db()
        self.assertEqual(categoria.nome, "Alimentação Atualizada")

        response = self.client.post(
            reverse("gestao_categorias"),
            {"delete_categoria": categoria.id},
            follow=True,
        )

        self.assertContains(response, "Categoria removida")
        self.assertFalse(Categoria.objects.filter(pk=categoria.pk).exists())

    def test_gestao_de_categorias_filtra_por_nome(self):
        self.client.force_login(self.user)

        Categoria.objects.create(nome="Alimentação")
        Categoria.objects.create(nome="Transporte")

        response = self.client.get(reverse("gestao_categorias"), {"q": "ali"})

        self.assertContains(response, "Alimentação")
        self.assertNotContains(response, "Transporte")

    def test_gestao_de_categorias_nao_remove_quando_ha_despesas_associadas(self):
        self.client.force_login(self.user)

        Despesa.objects.create(
            user=self.user,
            tipo=Despesa.SAIDA,
            categoria=self.categoria,
            valor="5.00",
            data="2024-01-04",
            descricao="Compras",
        )

        response = self.client.post(
            reverse("gestao_categorias"),
            {"delete_categoria": self.categoria.id},
            follow=True,
        )

        self.assertContains(response, "não pode ser removida")
        self.assertTrue(Categoria.objects.filter(pk=self.categoria.pk).exists())

    def test_obter_resumo_mensal_retorna_movimentos_e_totais(self):
        despesas = Despesa.objects.filter(user=self.user)

        movimentos, entradas, saidas, saldo = obter_resumo_mensal(despesas, 1, 2024)

        self.assertEqual(movimentos.count(), 1)
        self.assertEqual(entradas, Decimal("0.00"))
        self.assertEqual(saidas, Decimal("10.50"))
        self.assertEqual(saldo, Decimal("-10.50"))

    def test_obter_resumo_anual_retorna_movimentos_ordenados(self):
        despesas = Despesa.objects.filter(user=self.user)

        movimentos, entradas, saidas, saldo = obter_resumo_anual(despesas, 2024)

        self.assertEqual(movimentos.count(), 1)
        self.assertEqual(entradas, Decimal("0.00"))
        self.assertEqual(saidas, Decimal("10.50"))
        self.assertEqual(saldo, Decimal("-10.50"))
