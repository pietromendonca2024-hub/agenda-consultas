from django.urls import path
from . import views
urlpatterns = [
    path("", views.painel, name="painel"),
    path("consultas/", views.lista, name="lista"),
    path("consultas/nova/", views.editar, name="nova"),
    path("consultas/<int:pk>/", views.detalhe, name="detalhe"),
    path("consultas/<int:pk>/editar/", views.editar, name="editar"),
    path("consultas/<int:pk>/excluir/", views.excluir, name="excluir"),
    path("pacientes/", views.pacientes, name="pacientes"),
    path("pacientes/novo/", views.paciente_editar, name="paciente_novo"),
    path("pacientes/<int:pk>/editar/", views.paciente_editar, name="paciente_editar"),
    path("profissionais/", views.profissionais, name="profissionais"),
]
