from datetime import date, time, timedelta
from io import StringIO
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db.models.deletion import ProtectedError
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Paciente, Profissional, Consulta


class AgendaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser('equipe', 'equipe@example.com', 'SenhaTeste-912!')
        cls.paciente = Paciente.objects.create(nome='Ana Teste', nascimento=date(2000, 1, 1), telefone='21900000000')
        cls.outro_paciente = Paciente.objects.create(nome='Bruno Teste', nascimento=date(2001, 2, 2), telefone='21900000001')
        cls.profissional = Profissional.objects.create(nome='Marina', especialidade='Clínica geral', registro='DEMO-TESTE-1')
        cls.outro_profissional = Profissional.objects.create(nome='Rafael', especialidade='Odontologia', registro='DEMO-TESTE-2')

    def setUp(self):
        self.client.force_login(self.user)
        self.data = timezone.localdate() + timedelta(days=2)

    def dados(self, **overrides):
        data = dict(paciente=self.paciente, profissional=self.profissional, data=self.data,
                    inicio=time(9), fim=time(9, 30), status='agendada')
        data.update(overrides)
        return data

    def post_data(self, **overrides):
        data = dict(paciente=self.paciente.pk, profissional=self.profissional.pk, data=self.data.isoformat(),
                    inicio='09:00', fim='09:30', status='agendada', observacoes='Teste')
        data.update(overrides)
        return data

    def test_paginas_e_admin_renderizam(self):
        c = Consulta.objects.create(**self.dados())
        urls = ['/', '/consultas/', '/consultas/nova/', '/pacientes/', '/pacientes/novo/', '/profissionais/', '/admin/', '/admin/consultas/consulta/', '/admin/consultas/consulta/add/', f'/admin/consultas/consulta/{c.pk}/change/', f'/consultas/{c.pk}/', f'/consultas/{c.pk}/editar/', f'/consultas/{c.pk}/excluir/', f'/pacientes/{self.paciente.pk}/editar/']
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_crud_completo(self):
        r = self.client.post(reverse('nova'), self.post_data())
        c = Consulta.objects.get()
        self.assertRedirects(r, reverse('detalhe', args=[c.pk]))
        r = self.client.post(reverse('editar', args=[c.pk]), self.post_data(status='confirmada'))
        self.assertEqual(r.status_code, 302)
        c.refresh_from_db()
        self.assertEqual(c.status, 'confirmada')
        self.client.get(reverse('excluir', args=[c.pk]))
        self.assertTrue(Consulta.objects.filter(pk=c.pk).exists())
        r = self.client.post(reverse('excluir', args=[c.pk]))
        self.assertRedirects(r, reverse('lista'))
        self.assertFalse(Consulta.objects.exists())

    def test_sobreposicao_profissional(self):
        Consulta.objects.create(**self.dados())
        with self.assertRaisesMessage(ValidationError, 'profissional já possui'):
            Consulta.objects.create(**self.dados(paciente=self.outro_paciente, inicio=time(9, 15), fim=time(10)))

    def test_sobreposicao_paciente(self):
        Consulta.objects.create(**self.dados())
        with self.assertRaisesMessage(ValidationError, 'paciente já possui'):
            Consulta.objects.create(**self.dados(profissional=self.outro_profissional, inicio=time(8, 30), fim=time(9, 15)))

    def test_intervalo_englobando_consulta(self):
        Consulta.objects.create(**self.dados())
        with self.assertRaises(ValidationError):
            Consulta.objects.create(**self.dados(inicio=time(8), fim=time(10)))

    def test_intervalos_adjacentes_permitidos(self):
        Consulta.objects.create(**self.dados())
        Consulta.objects.create(**self.dados(inicio=time(9, 30), fim=time(10)))
        self.assertEqual(Consulta.objects.count(), 2)

    def test_cancelamento_libera_horario(self):
        c = Consulta.objects.create(**self.dados())
        c.status = 'cancelada'
        c.save()
        Consulta.objects.create(**self.dados())
        self.assertEqual(Consulta.objects.count(), 2)
        c.status = 'confirmada'
        with self.assertRaises(ValidationError):
            c.save()

    def test_edicao_mantendo_horario(self):
        c = Consulta.objects.create(**self.dados())
        c.observacoes = 'Contato confirmado'
        c.save()
        self.assertEqual(Consulta.objects.get().observacoes, 'Contato confirmado')

    def test_fim_invalido_e_fora_expediente(self):
        for inicio, fim in [(time(9), time(9)), (time(9), time(8)), (time(6), time(8)), (time(19), time(21))]:
            with self.subTest(inicio=inicio, fim=fim), self.assertRaises(ValidationError):
                Consulta.objects.create(**self.dados(inicio=inicio, fim=fim))

    def test_agendamento_passado_rejeitado(self):
        with self.assertRaises(ValidationError):
            Consulta.objects.create(**self.dados(data=timezone.localdate()-timedelta(days=1)))

    def test_realizada_futura_rejeitada(self):
        with self.assertRaises(ValidationError):
            Consulta.objects.create(**self.dados(status='realizada'))

    def test_historico_realizado_permitido(self):
        Consulta.objects.create(**self.dados(data=timezone.localdate()-timedelta(days=1), status='realizada'))
        self.assertEqual(Consulta.objects.count(), 1)

    def test_profissional_inativo(self):
        self.profissional.ativo = False
        self.profissional.save()
        with self.assertRaises(ValidationError):
            Consulta.objects.create(**self.dados())

    def test_formulario_mostra_conflito_sem_gravar(self):
        Consulta.objects.create(**self.dados())
        r = self.client.post(reverse('nova'), self.post_data(inicio='09:15', fim='10:00'))
        self.assertContains(r, 'profissional já possui')
        self.assertEqual(Consulta.objects.count(), 1)

    def test_admin_valida_conflito(self):
        Consulta.objects.create(**self.dados())
        r = self.client.post('/admin/consultas/consulta/add/', self.post_data(inicio='09:15', fim='10:00'))
        self.assertContains(r, 'profissional já possui')
        self.assertEqual(Consulta.objects.count(), 1)

    def test_busca_filtros_e_data_invalida(self):
        Consulta.objects.create(**self.dados())
        r = self.client.get('/consultas/', {'q': 'Ana', 'data': self.data.isoformat(), 'profissional': self.profissional.pk, 'status': 'agendada'})
        self.assertEqual(r.context['page_obj'].paginator.count, 1)
        self.assertEqual(self.client.get('/consultas/', {'q': 'inexistente'}).context['page_obj'].paginator.count, 0)
        r = self.client.get('/consultas/', {'data': 'invalida'})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context['form'].errors)

    def test_anonimo_redirecionado_e_nao_altera_banco(self):
        self.client.logout()
        for url in ['/', '/consultas/', '/pacientes/', '/profissionais/', '/consultas/nova/']:
            self.assertEqual(self.client.get(url).status_code, 302)
        self.client.post('/consultas/nova/', self.post_data())
        self.assertEqual(Consulta.objects.count(), 0)
        self.assertEqual(self.client.get('/entrar/').status_code, 200)

    def test_usuario_comum_negado(self):
        user = get_user_model().objects.create_user('visitante', password='senha-teste-324!')
        self.client.force_login(user)
        self.assertEqual(self.client.get('/').status_code, 403)
        self.client.logout()
        r = self.client.post('/entrar/', {'username': 'visitante', 'password': 'senha-teste-324!'})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_logout_funcionario(self):
        self.client.logout()
        r = self.client.post('/entrar/', {'username': 'equipe', 'password': 'SenhaTeste-912!'})
        self.assertRedirects(r, '/')
        self.assertEqual(self.client.get('/sair/').status_code, 405)
        self.assertRedirects(self.client.post('/sair/'), '/entrar/')

    def test_csrf_obrigatorio(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post('/consultas/nova/', self.post_data()).status_code, 403)

    def test_paciente_cadastro_edicao_e_validacao(self):
        dados = {'nome': 'Carla Teste', 'nascimento': '1999-10-10', 'telefone': '(21) 90000-0000', 'email': 'carla@example.com'}
        self.assertRedirects(self.client.post('/pacientes/novo/', dados), '/pacientes/')
        p = Paciente.objects.get(nome='Carla Teste')
        dados['nome'] = 'Carla Atualizada'
        self.client.post(f'/pacientes/{p.pk}/editar/', dados)
        p.refresh_from_db()
        self.assertEqual(p.nome, 'Carla Atualizada')
        dados['nascimento'] = (timezone.localdate()+timedelta(days=1)).isoformat()
        r = self.client.post('/pacientes/novo/', dados)
        self.assertContains(r, 'nascimento não pode estar no futuro')

    def test_protect_relacionamentos(self):
        Consulta.objects.create(**self.dados())
        for obj in [self.paciente, self.profissional]:
            with self.assertRaises(ProtectedError):
                obj.delete()

    def test_paginacao_e_registro_inexistente(self):
        for i in range(13):
            Consulta.objects.create(**self.dados(data=self.data+timedelta(days=i)))
        r = self.client.get('/consultas/?page=2')
        self.assertEqual(len(r.context['page_obj']), 3)
        self.assertEqual(self.client.get('/consultas/99999/').status_code, 404)

    def test_demo_idempotente(self):
        call_command('popular_demo', stdout=StringIO())
        self.assertEqual(Consulta.objects.count(), 16)
        call_command('popular_demo', stdout=StringIO())
        self.assertEqual(Consulta.objects.count(), 16)
