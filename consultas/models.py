from datetime import datetime, time
from django.db import models, transaction
from django.db.models import Q, F
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone

class Paciente(models.Model):
    nome = models.CharField("nome completo", max_length=120)
    nascimento = models.DateField("data de nascimento")
    telefone = models.CharField(max_length=20, validators=[RegexValidator(r"^[0-9()+ \-]{10,20}$", "Informe um telefone válido com DDD.")])
    email = models.EmailField("e-mail", blank=True)
    class Meta:
        ordering = ["nome"]
    def __str__(self):
        return f"{self.nome} • #{self.pk}" if self.pk else self.nome
    def clean(self):
        if self.nascimento and self.nascimento > timezone.localdate():
            raise ValidationError({"nascimento": "O nascimento não pode estar no futuro."})

class Profissional(models.Model):
    nome = models.CharField(max_length=120)
    especialidade = models.CharField(max_length=80)
    registro = models.CharField("registro profissional", max_length=40, unique=True)
    ativo = models.BooleanField(default=True)
    class Meta:
        ordering = ["nome"]
        verbose_name_plural = "profissionais"
    def __str__(self):
        return f"{self.nome} — {self.especialidade}"

class Consulta(models.Model):
    class Status(models.TextChoices):
        AGENDADA = "agendada", "Agendada"
        CONFIRMADA = "confirmada", "Confirmada"
        REALIZADA = "realizada", "Realizada"
        CANCELADA = "cancelada", "Cancelada"
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, related_name="consultas")
    profissional = models.ForeignKey(Profissional, on_delete=models.PROTECT, related_name="consultas")
    data = models.DateField("data da consulta", db_index=True)
    inicio = models.TimeField("horário de início")
    fim = models.TimeField("horário de término")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.AGENDADA)
    observacoes = models.TextField("observações administrativas", blank=True, max_length=1000, help_text="Use apenas informações do agendamento, sem prontuário clínico.")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["data", "inicio", "pk"]
        verbose_name_plural = "consultas"
        constraints = [models.CheckConstraint(condition=Q(fim__gt=F("inicio")), name="consulta_fim_apos_inicio")]
    def __str__(self):
        return f"{self.paciente.nome} — {self.data:%d/%m/%Y} às {self.inicio:%H:%M}"
    def clean(self):
        super().clean()
        if not all([self.data, self.inicio, self.fim]):
            return
        if self.fim <= self.inicio:
            raise ValidationError({"fim": "O término precisa ser depois do início."})
        if self.inicio < time(7) or self.fim > time(20):
            raise ValidationError("O horário de atendimento é das 07:00 às 20:00.")
        if self.inicio.second or self.fim.second:
            raise ValidationError("Informe horários sem segundos.")
        start = timezone.make_aware(datetime.combine(self.data, self.inicio))
        end = timezone.make_aware(datetime.combine(self.data, self.fim))
        old = type(self).objects.filter(pk=self.pk).first() if self.pk else None
        changed = not old or (old.data, old.inicio, old.fim, old.profissional_id, old.paciente_id) != (self.data, self.inicio, self.fim, self.profissional_id, self.paciente_id)
        reactivated = old and old.status in [self.Status.CANCELADA, self.Status.REALIZADA] and self.status in [self.Status.AGENDADA, self.Status.CONFIRMADA]
        if self.status in [self.Status.AGENDADA, self.Status.CONFIRMADA] and (changed or reactivated) and start < timezone.now():
            raise ValidationError({"data": "Escolha uma data e um horário futuros para agendar."})
        if self.status == self.Status.REALIZADA and end > timezone.now():
            raise ValidationError({"status": "Uma consulta futura não pode ser marcada como realizada."})
        if self.profissional_id and self.status in [self.Status.AGENDADA, self.Status.CONFIRMADA] and changed and not self.profissional.ativo:
            raise ValidationError({"profissional": "Escolha um profissional ativo."})
        # Intervalos [início, fim): uma consulta pode começar quando a anterior termina.
        if self.status != self.Status.CANCELADA:
            overlaps = type(self).objects.filter(data=self.data, inicio__lt=self.fim, fim__gt=self.inicio).exclude(pk=self.pk).exclude(status=self.Status.CANCELADA)
            if self.profissional_id and overlaps.filter(profissional_id=self.profissional_id).exists():
                raise ValidationError("Este profissional já possui uma consulta nesse intervalo.")
            if self.paciente_id and overlaps.filter(paciente_id=self.paciente_id).exists():
                raise ValidationError("Este paciente já possui uma consulta nesse intervalo.")
    def save(self, *args, **kwargs):
        # SQLite usa BEGIN IMMEDIATE: verificação e escrita são serializadas.
        with transaction.atomic():
            self.full_clean()
            return super().save(*args, **kwargs)
