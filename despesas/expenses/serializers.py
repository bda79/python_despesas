from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Categoria, Despesa, Compartilhamento


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"


class DespesaSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(
        source="categoria.nome",
        read_only=True,
    )

    user = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    # pode aceitar string ou id
    categoria_input = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Despesa
        fields = [
            "id",
            "tipo",
            "categoria",
            "categoria_nome",
            "categoria_input",
            "valor",
            "data",
            "descricao",
            "user",
        ]

    def create(self, validated_data):
        categoria_input = validated_data.pop("categoria_input", None)
        user = self.context["request"].user

        # se veio texto → cria ou obtém categoria
        if categoria_input:
            categoria, _ = Categoria.objects.get_or_create(
                nome__iexact=categoria_input,
                defaults={"nome": categoria_input},
            )
            validated_data["categoria"] = categoria

        validated_data["user"] = user
        return super().create(validated_data)


class CompartilhamentoSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(
        source="owner.username",
        read_only=True,
    )

    shared_user = serializers.CharField(
        source="shared_user.username",
        read_only=True,
    )

    class Meta:
        model = Compartilhamento
        fields = [
            "id",
            "owner",
            "shared_user",
            "created_at",
        ]
        model = Despesa
        fields = [
            "id",
            "tipo",
            "categoria",
            "categoria_nome",
            "valor",
            "data",
            "descricao",
        ]


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
        )
        return user
