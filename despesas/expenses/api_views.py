from django.contrib.auth.models import User

# from django.contrib.auth.hashers import make_password
from django.db.models import Sum, FloatField, Q
from django.db.models.functions import Cast
from django.utils import timezone

from rest_framework import generics, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from decouple import config

from .models import Categoria, Compartilhamento, Despesa, PasswordResetToken

from .serializers import (
    CategoriaSerializer,
    CompartilhamentoSerializer,
    DespesaSerializer,
    RegisterSerializer,
)

from .services.email_service import send_password_reset_email


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
        username = request.data.get("username")
        email = request.data.get("email")

        # validações manuais antes do serializer
        if User.objects.filter(username=username).exists():
            return Response({"message": "Username já existe"}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({"message": "Email já está em uso"}, status=400)

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Conta criada com sucesso",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=201,
            )

        return Response(
            {"message": "Erro no registo", "errors": serializer.errors}, status=400
        )


class RequestPasswordResetAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.filter(email=email).first()

            # sempre resposta igual (segurança)
            if not user:
                return Response({"message": "Se o email existir, foi enviado link."})

            PasswordResetToken.objects.filter(
                user=user,
                used=False,
            ).delete()

            token = PasswordResetToken.objects.create(user=user)

            reset_link = f"{config('FRONTEND_URL')}/reset-password?token={token.token}"

            send_password_reset_email(email, reset_link)

        except Exception as e:
            print("EMAIL ERROR:", e)

        return Response({"message": "Se o email existir, foi enviado link."})


class ConfirmPasswordResetAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            token_value = request.data.get("token")
            password = request.data.get("password")

            if not token_value or not password:
                return Response(
                    {"message": "Token e password são obrigatórios"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = PasswordResetToken.objects.filter(
                token=token_value, used=False
            ).first()

            if not token or not token.is_valid():
                return Response(
                    {"message": "Token inválido ou expirado"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = token.user

            # forma correta Django
            user.set_password(password)
            user.save()

            token.used = True
            token.save()

            return Response(
                {"message": "Password alterada com sucesso"}, status=status.HTTP_200_OK
            )

        except Exception as e:
            print("CONFIRM PASSWORD RESET ERROR:", e)
            return Response(
                {"message": "Erro interno no servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
    permission_classes = [AllowAny]

    serializer_class = CustomTokenObtainPairSerializer


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return Response({"message": "Refresh token obrigatório"}, status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"success": True})

        except Exception:
            return Response({"error": "Invalid token"}, status=400)
