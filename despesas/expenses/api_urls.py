from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .api_views import (
    LogoutAPIView,
    MeAPIView,
    DespesaListCreateAPIView,
    DespesaDetailAPIView,
    DashboardAPIView,
    RegisterAPIView,
    RequestPasswordResetAPIView,
    ResumoMensalAPIView,
    ResumoAnualAPIView,
    CompartilhamentoAPIView,
    CategoriaListAPIView,
    ConfirmPasswordResetAPIView,
    CustomTokenObtainPairView,
)

urlpatterns = [
    # JWT
    path("token/", CustomTokenObtainPairView.as_view()),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    # API
    path(
        "categorias/",
        CategoriaListAPIView.as_view(),
        name="api_categorias",
    ),
    path(
        "despesas/",
        DespesaListCreateAPIView.as_view(),
    ),
    path(
        "despesas/<int:pk>/",
        DespesaDetailAPIView.as_view(),
    ),
    path(
        "dashboard/",
        DashboardAPIView.as_view(),
    ),
    path(
        "resumo-mensal/",
        ResumoMensalAPIView.as_view(),
    ),
    path(
        "resumo-anual/",
        ResumoAnualAPIView.as_view(),
    ),
    path(
        "partilha/",
        CompartilhamentoAPIView.as_view(),
    ),
    path(
        "register/",
        RegisterAPIView.as_view(),
    ),
    path("password-reset/request/", RequestPasswordResetAPIView.as_view()),
    path("password-reset/confirm/", ConfirmPasswordResetAPIView.as_view()),
    path("logout/", LogoutAPIView.as_view()),
    path(
        "me/",
        MeAPIView.as_view(),
        name="api_me",
    ),
]
