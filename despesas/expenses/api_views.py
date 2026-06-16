from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db.models import Sum, FloatField, Q
from django.db.models.functions import Cast
from django.utils import timezone

from rest_framework import generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Categoria, Compartilhamento, Despesa, PasswordResetToken

from .serializers import (
    CategoriaSerializer,
    CompartilhamentoSerializer,
    DespesaSerializer,
    RegisterSerializer,
)


class CategoriaListAPIView(generics.ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
            }
        )


class DespesaListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DespesaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        compartilhamento = Compartilhamento.objects.filter(shared_user=user).first()

        tem_partilha = compartilhamento is not None
        ver_conjunto = self.request.GET.get("shared") == "1" and tem_partilha

        if ver_conjunto:
            qs = Despesa.objects.filter(Q(user=user) | Q(user=compartilhamento.owner))
        else:
            qs = Despesa.objects.filter(user=user)

        # ───────── SEARCH ─────────
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(descricao__icontains=q)
                | Q(categoria__nome__icontains=q)
                | Q(tipo__icontains=q)
            )

        # ───────── FILTROS ─────────
        mes = self.request.GET.get("mes")
        ano = self.request.GET.get("ano")
        categoria = self.request.GET.get("categoria")

        if mes:
            qs = qs.filter(data__month=mes)

        if ano:
            qs = qs.filter(data__year=ano)

        if categoria:
            qs = qs.filter(categoria__nome__icontains=categoria)

        return qs.order_by("-data")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DespesaDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DespesaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Despesa.objects.filter(user=self.request.user)


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        compartilhamento = Compartilhamento.objects.filter(
            shared_user=request.user
        ).first()

        tem_partilha = compartilhamento is not None

        ver_conjunto = request.GET.get("shared") == "1" and tem_partilha

        if ver_conjunto:
            despesas = Despesa.objects.filter(
                Q(user=request.user) | Q(user=compartilhamento.owner),
                tipo="saida",
            )
        else:
            despesas = Despesa.objects.filter(
                user=request.user,
                tipo="saida",
            )

        total = despesas.aggregate(Sum("valor"))["valor__sum"] or 0

        categorias = despesas.values("categoria__nome").annotate(
            total=Cast(
                Sum("valor"),
                FloatField(),
            )
        )

        return Response(
            {
                "total": total,
                "categorias": categorias,
            }
        )


class ResumoMensalAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        hoje = timezone.now()

        mes = int(request.GET.get("mes", hoje.month))
        ano = int(request.GET.get("ano", hoje.year))

        user = request.user

        compartilhamento = Compartilhamento.objects.filter(shared_user=user).first()

        tem_partilha = compartilhamento is not None
        ver_conjunto = request.GET.get("shared") == "1" and tem_partilha

        if ver_conjunto:
            qs = Despesa.objects.filter(
                Q(user=user) | Q(user=compartilhamento.owner),
                data__month=mes,
                data__year=ano,
            )
        else:
            qs = Despesa.objects.filter(
                user=user,
                data__month=mes,
                data__year=ano,
            )

        # ─────────────────────────────
        # SEARCH (opcional)
        # ─────────────────────────────
        q = request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(descricao__icontains=q)
                | Q(categoria__nome__icontains=q)
                | Q(tipo__icontains=q)
            )

        entradas = qs.filter(tipo="entrada").aggregate(Sum("valor"))["valor__sum"] or 0
        saidas = qs.filter(tipo="saida").aggregate(Sum("valor"))["valor__sum"] or 0

        return Response(
            {
                "mes": mes,
                "ano": ano,
                "entradas": entradas,
                "saidas": saidas,
                "saldo": entradas - saidas,
            }
        )


class ResumoAnualAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        hoje = timezone.now()
        ano = int(request.GET.get("ano", hoje.year))

        user = request.user

        compartilhamento = Compartilhamento.objects.filter(shared_user=user).first()

        tem_partilha = compartilhamento is not None
        ver_conjunto = request.GET.get("shared") == "1" and tem_partilha

        if ver_conjunto:
            qs = Despesa.objects.filter(
                Q(user=user) | Q(user=compartilhamento.owner),
                data__year=ano,
            )
        else:
            qs = Despesa.objects.filter(
                user=user,
                data__year=ano,
            )

        # ─────────────────────────────
        # SEARCH
        # ─────────────────────────────
        q = request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(descricao__icontains=q)
                | Q(categoria__nome__icontains=q)
                | Q(tipo__icontains=q)
            )

        entradas = qs.filter(tipo="entrada").aggregate(Sum("valor"))["valor__sum"] or 0
        saidas = qs.filter(tipo="saida").aggregate(Sum("valor"))["valor__sum"] or 0

        return Response(
            {
                "ano": ano,
                "entradas": entradas,
                "saidas": saidas,
                "saldo": entradas - saidas,
            }
        )


class CompartilhamentoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        partilha = Compartilhamento.objects.filter(owner=request.user).first()

        if not partilha:
            return Response(None)

        return Response(CompartilhamentoSerializer(partilha).data)

    def post(self, request):

        identificador = request.data.get("identificador")

        user = User.objects.filter(
            Q(email=identificador) | Q(username=identificador)
        ).first()

        if not user:
            return Response(
                {"error": "Utilizador não encontrado."},
                status=400,
            )

        partilha = Compartilhamento.objects.create(
            owner=request.user,
            shared_user=user,
        )

        return Response(CompartilhamentoSerializer(partilha).data)

    def delete(self, request):

        Compartilhamento.objects.filter(owner=request.user).delete()

        return Response({"success": True})


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                status=201,
            )

        return Response(serializer.errors, status=400)


class RequestPasswordResetAPIView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")

        user = User.objects.filter(email=email).first()

        # SEMPRE resposta igual (segurança)
        if not user:
            return Response({"message": "Se o email existir, foi enviado link."})

        token = PasswordResetToken.objects.create(user=user)

        return Response({"message": "OK", "token": str(token.token)})


class ConfirmPasswordResetAPIView(APIView):
    permission_classes = []

    def post(self, request):
        token_value = request.data.get("token")
        new_password = request.data.get("password")

        token = PasswordResetToken.objects.filter(token=token_value, used=False).first()

        if not token or not token.is_valid():
            return Response({"error": "Token inválido"}, status=400)

        user = token.user
        user.password = make_password(new_password)
        user.save()

        token.used = True
        token.save()

        return Response({"message": "Password alterada com sucesso"})


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):

        login_input = attrs.get("username")
        # password = attrs.get("password")

        user = (
            User.objects.filter(email=login_input).first()
            or User.objects.filter(username=login_input).first()
        )

        if user:
            attrs["username"] = user.username

        return super().validate(attrs)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            refresh_token = request.data["refresh"]

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"success": True})

        except Exception:
            return Response({"error": "Invalid token"}, status=400)
