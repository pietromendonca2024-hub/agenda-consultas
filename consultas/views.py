from functools import wraps
from urllib.parse import quote
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import ConsultaForm, PacienteForm, FiltroForm
from .models import Consulta, Paciente, Profissional

def funcionario(view):
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper

@funcionario
def painel(request):
    hoje = timezone.localdate()
    consultas = Consulta.objects.select_related("paciente", "profissional")
    resumo = consultas.aggregate(total=Count("pk"), agendadas=Count("pk", filter=Q(status__in=["agendada", "confirmada"])), realizadas=Count("pk", filter=Q(status="realizada")), canceladas=Count("pk", filter=Q(status="cancelada")))
    proximas = consultas.filter(Q(data__gt=hoje) | Q(data=hoje, inicio__gte=timezone.localtime().time()), status__in=["agendada", "confirmada"])[:5]
    return render(request, "consultas/painel.html", {"hoje": hoje, "resumo": resumo, "agenda": consultas.filter(data=hoje), "proximas": proximas, "pacientes": Paciente.objects.count(), "profissionais": Profissional.objects.filter(ativo=True).count()})

@funcionario
def lista(request):
    form = FiltroForm(request.GET)
    qs = Consulta.objects.select_related("paciente", "profissional")
    if form.is_valid():
        for campo in ["data", "profissional", "status"]:
            if form.cleaned_data[campo]:
                qs = qs.filter(**{campo: form.cleaned_data[campo]})
        if form.cleaned_data["q"]:
            qs = qs.filter(paciente__nome__icontains=form.cleaned_data["q"])
    else:
        qs = qs.none()
    params = request.GET.copy()
    params.pop("page", None)
    page = Paginator(qs, 10).get_page(request.GET.get("page"))
    return render(request, "consultas/lista.html", {"form": form, "page_obj": page, "query": params.urlencode()})

@funcionario
def detalhe(request, pk):
    return render(request, "consultas/detalhe.html", {"consulta": get_object_or_404(Consulta.objects.select_related("paciente", "profissional"), pk=pk)})

@funcionario
def editar(request, pk=None):
    consulta = get_object_or_404(Consulta, pk=pk) if pk else None
    form = ConsultaForm(request.POST or None, instance=consulta)
    if request.method == "POST" and form.is_valid():
        try:
            consulta = form.save()
        except ValidationError as exc:
            form.add_error(None, "; ".join(exc.messages))
        else:
            messages.success(request, "Consulta atualizada com sucesso." if pk else "Consulta agendada com sucesso.")
            return redirect("detalhe", pk=consulta.pk)
    return render(request, "consultas/formulario.html", {"form": form, "titulo": "Editar consulta" if pk else "Nova consulta", "subtitulo": "Organize o atendimento com todos os dados em um só lugar.", "consulta_form": True})

@funcionario
def excluir(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk)
    if request.method == "POST":
        consulta.delete()
        messages.success(request, "Consulta excluída com sucesso.")
        return redirect("lista")
    return render(request, "consultas/excluir.html", {"consulta": consulta})

@funcionario
def pacientes(request):
    q = request.GET.get("q", "")[:120]
    qs = Paciente.objects.filter(nome__icontains=q)
    return render(request, "consultas/pacientes.html", {"page_obj": Paginator(qs, 12).get_page(request.GET.get("page")), "q": q, "query": "q=" + quote(q)})

@funcionario
def paciente_editar(request, pk=None):
    paciente = get_object_or_404(Paciente, pk=pk) if pk else None
    form = PacienteForm(request.POST or None, instance=paciente)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Paciente salvo com sucesso.")
        return redirect("pacientes")
    return render(request, "consultas/formulario.html", {"form": form, "titulo": "Editar paciente" if pk else "Novo paciente", "subtitulo": "Dados de contato para facilitar o atendimento."})

@funcionario
def profissionais(request):
    return render(request, "consultas/profissionais.html", {"profissionais": Profissional.objects.all()})
