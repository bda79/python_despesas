from django.contrib import admin
from .models import Categoria, Despesa, Compartilhamento

admin.site.register(Categoria)
admin.site.register(Despesa)
admin.site.register(Compartilhamento)

# Register your models here.
