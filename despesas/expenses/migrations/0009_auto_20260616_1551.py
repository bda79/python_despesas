from django.db import migrations
from django.contrib.auth.hashers import make_password


def reset_admin_password(apps, schema_editor):
    User = apps.get_model("auth", "User")

    User.objects.filter(username="admin").update(
        password=make_password("NovaPassword123!")
    )


class Migration(migrations.Migration):

    dependencies = [
        ("expenses", "0008_alter_despesa_options"),
    ]

    operations = [
        migrations.RunPython(reset_admin_password),
    ]
