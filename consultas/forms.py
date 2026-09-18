from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Consulta, Paciente, Profissional

class EstiloForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-select" if isinstance(field.widget, forms.Select) else "form-control"

class LoginForm(EstiloForm, AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise ValidationError("Acesso permitido apenas para funcionários autorizados.")

class ConsultaForm(EstiloForm, forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ["paciente", "profissional", "data", "inicio", "fim", "status", "observacoes"]
        widgets = {"data": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}), "inicio": forms.TimeInput(format="%H:%M", attrs={"type": "time"}), "fim": forms.TimeInput(format="%H:%M", attrs={"type": "time"}), "observacoes": forms.Textarea(attrs={"rows": 3})}

class PacienteForm(EstiloForm, forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ["nome", "nascimento", "telefone", "email"]
        widgets = {"nascimento": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})}

class FiltroForm(EstiloForm, forms.Form):
    q = forms.CharField(label="Buscar paciente", required=False, max_length=120, widget=forms.TextInput(attrs={"placeholder": "Nome do paciente…"}))
    data = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    profissional = forms.ModelChoiceField(queryset=Profissional.objects.all(), required=False, empty_label="Todos os profissionais")
    status = forms.ChoiceField(required=False, choices=[("", "Todos os status"), *Consulta.Status.choices])
