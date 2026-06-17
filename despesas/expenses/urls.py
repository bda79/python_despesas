from django.urls import path, include
from django.contrib.auth import views as auth_views
from .forms import CustomSetPasswordForm

from . import views

urlpatterns = [
    # AUTH
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    # RESET PASSWORD
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            form_class=CustomSetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # APP
    path("", views.lista_despesas, name="lista"),
    path("nova/", views.nova_despesa, name="nova_despesa"),
    path("editar/<int:id>/", views.editar_despesa, name="editar"),
    path("apagar/<int:id>/", views.apagar_despesa, name="apagar"),
    path("resumo-mensal/", views.resumo_mensal, name="resumo_mensal"),
    path("resumo-anual/", views.resumo_anual, name="resumo_anual"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("configuracoes/", views.configuracoes, name="configuracoes"),
    path("api/despesas/", views.api_despesas, name="api_despesas"),
    # SESSION
    path("keep_alive/", views.keep_alive, name="keep_alive"),
    path("__reload__/", include("django_browser_reload.urls")),
    path("smtp-test/", views.smtp_test),
]
