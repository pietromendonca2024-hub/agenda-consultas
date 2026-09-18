from django.contrib import admin
from .models import Consulta, Paciente, Profissional
@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ("paciente", "profissional", "data", "inicio", "fim", "status")
    list_filter = ("status", "data", "profissional")
    search_fields = ("paciente__nome", "profissional__nome")
    autocomplete_fields = ("paciente", "profissional")
    date_hierarchy = "data"
    readonly_fields = ("criado_em", "atualizado_em")
    list_select_related = ("paciente", "profissional")
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "nascimento", "telefone", "email")
    search_fields = ("nome", "telefone")
@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = ("nome", "especialidade", "registro", "ativo")
    list_filter = ("especialidade", "ativo")
    search_fields = ("nome", "especialidade", "registro")
