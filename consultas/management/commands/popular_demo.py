from datetime import date, datetime, time, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from consultas.models import Paciente, Profissional, Consulta

class Command(BaseCommand):
    help = "Cadastra 12 pacientes fictícios, 4 profissionais e 16 consultas demonstrativas."
    @transaction.atomic
    def handle(self, *args, **options):
        if Consulta.objects.exists():
            self.stdout.write("Já existem consultas. Nenhum dado foi alterado.")
            return
        nomes = ["Ana Clara Lima", "Bruno Martins", "Camila Souza", "Daniel Oliveira", "Elisa Fernandes", "Felipe Rocha", "Gabriela Alves", "Henrique Costa", "Isabela Santos", "João Pedro Melo", "Larissa Ribeiro", "Mateus Pereira"]
        pacientes=[]
        for i, nome in enumerate(nomes):
            obj, _ = Paciente.objects.get_or_create(nome=nome, nascimento=date(1985+i, (i%12)+1, 10), defaults={"telefone": "(21) 90000-0000", "email": f"paciente{i+1}@example.com"})
            pacientes.append(obj)
        equipe=[]
        for nome, area, registro in [("Marina Azevedo", "Clínica geral", "CRM-DEMO-001"), ("Rafael Nogueira", "Odontologia", "CRO-DEMO-002"), ("Beatriz Duarte", "Dermatologia", "CRM-DEMO-003"), ("Lucas Tavares", "Cardiologia", "CRM-DEMO-004")]:
            obj, _ = Profissional.objects.get_or_create(registro=registro, defaults={"nome": nome, "especialidade": area})
            equipe.append(obj)
        hoje=timezone.localdate()
        for i in range(16):
            if i < 4:
                data=hoje-timedelta(days=2)
                hora=9+i
                status="realizada" if i<3 else "cancelada"
            elif i<10:
                data=hoje
                hora=8+(i-4)*2
                fim=timezone.make_aware(datetime.combine(data,time(hora,30)))
                inicio=timezone.make_aware(datetime.combine(data,time(hora)))
                status="realizada" if fim<=timezone.now() else ("cancelada" if inicio<=timezone.now() else "confirmada")
            else:
                data=hoje+timedelta(days=1+(i-10)//3)
                hora=9+((i-10)%3)*2
                status="agendada" if i%2 else "confirmada"
            Consulta.objects.create(paciente=pacientes[i%12], profissional=equipe[i%4], data=data, inicio=time(hora), fim=time(hora,30), status=status, observacoes="Cadastro fictício para apresentação acadêmica.")
        self.stdout.write(self.style.SUCCESS("16 consultas, 12 pacientes e 4 profissionais de demonstração cadastrados."))
