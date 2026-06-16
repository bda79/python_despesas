from django.contrib.auth import get_user_model


def create_admin():
    User = get_user_model()

    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin", email="admin@site.com", password="NovaPassword123!"
        )
        print("Superuser criado com sucesso")
    else:
        print("Superuser já existe")
