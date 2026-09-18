# Agenda de Consultas — Clínica Saúde Viva

Projeto 2 · Programador Back-End Python · Desenvolvimento Web com Django.
Projeto acadêmico independente, inspirado no enunciado fornecido; não é um produto oficial do Senac.

## Começar no Windows (jeito fácil)

1. Extraia o ZIP inteiro. Não execute os arquivos dentro do ZIP.
2. Instale Python 3.10 ou superior. Python 3.12 ou 3.13 são boas opções para este projeto. Inclua o Python Launcher e a opção de adicionar ao PATH.
3. Abra a pasta `agenda_consultas` e execute **iniciar.bat** com dois cliques.
4. Na primeira execução, a instalação precisa de internet. O programa prepara o ambiente e pede que você crie seu próprio usuário e senha de administrador. A senha não aparece enquanto é digitada.
5. Abra **http://127.0.0.1:8000/** e entre com a conta criada.
6. O Django Admin fica em **http://127.0.0.1:8000/admin/**.
7. Deixe a janela aberta. Para encerrar, use Ctrl+C. Depois, basta abrir `iniciar.bat` novamente.

O banco SQLite já acompanha o projeto com **16 consultas fictícias, 12 pacientes e 4 profissionais**. Não acompanha nenhuma senha pronta. O comando de demonstração não apaga nem duplica consultas existentes.

## Rodar no VS Code — PowerShell

Abra a pasta que contém `manage.py` no VS Code. No terminal integrado:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py createsuperuser
.venv\Scripts\python.exe manage.py runserver
```

Acesse http://127.0.0.1:8000/. Não é necessário ativar o ambiente virtual, portanto não é preciso alterar a política de scripts do PowerShell.

Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

## O que está incluído

- Django 5.2, SQLite e Bootstrap 5, com CSS/JS locais: a interface não depende de CDN.
- Login e logout, com acesso somente a usuários ativos marcados como membros da equipe (`is_staff`).
- Dashboard com totais gerais, agenda de hoje e próximos atendimentos.
- CRUD completo de consultas: criar, listar, visualizar detalhes, editar e excluir com confirmação.
- Busca por paciente, filtros de data/profissional/status e paginação.
- Cadastro e edição de pacientes pela interface.
- Listagem de profissionais; cadastro e administração pelo Django Admin.
- Status agendada, confirmada, realizada e cancelada.
- Validação de horários sobrepostos para o profissional E para o paciente, inclusive no Admin.
- Templates reutilizáveis, layout responsivo, mensagens de retorno e proteção CSRF.
- Migrations, banco preenchido e testes automatizados.

## Regras de negócio

1. O atendimento ocorre das 07:00 às 20:00. A consulta precisa terminar depois de começar, no mesmo dia.
2. Novos agendamentos e reagendamentos precisam ser futuros. Uma consulta antiga já cadastrada pode ser editada sem obrigar a alterar seu horário, desde que as demais regras sejam atendidas.
3. Consultas futuras não podem ser marcadas como realizadas. Consultas históricas realizadas ou canceladas podem ser registradas.
4. Consultas não canceladas não podem se sobrepor para o mesmo profissional ou paciente. Consultas encostadas (09:00–09:30 e 09:30–10:00) são permitidas.
5. Cancelar libera o horário e preserva o histórico. Excluir remove o registro após confirmação por POST.
6. Profissionais inativos não recebem novos agendamentos.
7. Pacientes e profissionais usados em consultas são protegidos contra exclusão pelo relacionamento `PROTECT`.
8. Todos os funcionários autorizados têm acesso operacional às consultas e pacientes. As permissões do Django Admin são separadas; o superusuário tem acesso completo.

Os horários são interpretados no fuso **America/Sao_Paulo**. Os dados de exemplo têm datas relativas ao dia em que foram gerados; com o passar dos dias, deixam de aparecer na agenda de hoje, mas continuam em Consultas.

## Estrutura

```text
agenda_consultas/
  manage.py
  requirements.txt
  db.sqlite3
  iniciar.bat
  config/                  configuração, URLs principais, ASGI e WSGI
  consultas/
    models.py              Paciente, Profissional, Consulta e validações
    forms.py               ModelForms e formulário de filtros
    views.py               páginas e operações do CRUD
    urls.py                rotas da aplicação
    admin.py               administração dos modelos
    tests.py               testes de regras e fluxos
    migrations/            histórico de criação do banco
    management/commands/   popular_demo
  templates/
    base.html              estrutura compartilhada
    registration/          tela de login
    consultas/             páginas e componentes reutilizáveis
  static/
    css/style.css          identidade visual e responsividade
    vendor/                Bootstrap 5 local
  docs/
    ROTEIRO_APRESENTACAO.md
    VALIDACAO.md
```

## Testar e conferir

```powershell
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py test
```

Os testes usam um banco isolado e não alteram o banco de demonstração.

Para criar os dados em uma cópia vazia do projeto, execute `python manage.py migrate` e `python manage.py popular_demo`. Esse comando só popula se ainda não houver consultas; não remove registros existentes.

## Dúvidas comuns

- **`No module named django`**: use o Python da `.venv`, conforme os comandos acima.
- **Erro de porta em uso**: execute `python manage.py runserver 8001` com o Python do ambiente e abra http://127.0.0.1:8001/.
- **Senha esquecida**: execute `python manage.py changepassword SEU_USUARIO` com o Python do ambiente.
- **Nenhum profissional/paciente na seleção**: execute `popular_demo` em um banco sem consultas ou cadastre pelo Admin.
- **Sem consultas hoje**: as datas demonstrativas podem ser anteriores ao dia da apresentação. Crie novas consultas para a data atual/futura; os registros antigos permanecem na listagem.
- **Sem acesso ao Admin**: use a conta criada por `createsuperuser`, ou configure os grupos e permissões da equipe.

## Escopo e decisões técnicas

Este pacote é para execução local e avaliação acadêmica. Não contém prontuário, envio de mensagens, pagamentos ou agenda integrada a serviços externos. Não publique o `runserver` na internet. Para uso real são necessárias configuração de produção, HTTPS, política de acesso, backups e tratamento adequado de dados pessoais. As observações são administrativas.

O `save()` de Consulta valida e grava dentro de uma transação. O SQLite está configurado com `transaction_mode='IMMEDIATE'` para serializar a validação e a escrita. O sistema não usa `bulk_create()`/`QuerySet.update()` para consultas, pois essas operações ignoram o `save()` e as regras Python. Uma restrição no banco também garante fim maior que início.

A chave Django local é gerada na primeira inicialização e fica em `.secret_key`. Em produção, use `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0` e `DJANGO_ALLOWED_HOSTS`. O ZIP não inclui chave nem conta de administrador.

## Referências

- Django 5.2 — ModelForms: https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/
- Django 5.2 — Tutorial: https://docs.djangoproject.com/en/5.2/intro/tutorial01/
- Bootstrap 5: https://getbootstrap.com/docs/5.3/

Bootstrap é distribuído sob a licença MIT; consulte `static/vendor/LICENSE-bootstrap.txt`.
