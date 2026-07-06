from django.db.models import Q

from ..models import Compartilhamento, Despesa


def obter_estado_partilha(request):
    compartilhamento = (
        Compartilhamento.objects.select_related("owner")
        .filter(shared_user=request.user)
        .first()
    )

    tem_partilha = compartilhamento is not None
    ver_conjunto = request.GET.get("shared") == "1" and tem_partilha

    return compartilhamento, tem_partilha, ver_conjunto


def obter_despesas(request):
    compartilhamento, tem_partilha, ver_conjunto = obter_estado_partilha(request)

    if ver_conjunto:
        qs = Despesa.objects.select_related("categoria", "user").filter(
            Q(user=request.user) | Q(user=compartilhamento.owner)
        )
    else:
        qs = Despesa.objects.select_related("categoria", "user").filter(
            user=request.user
        )

    return qs, tem_partilha, ver_conjunto
