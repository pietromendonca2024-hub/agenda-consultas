# Roteiro de apresentação — 5 a 8 minutos

## 1. Problema e proposta (40 segundos)
“A Clínica Saúde Viva usava uma agenda em papel e tinha dificuldade para localizar consultas e evitar conflitos. Desenvolvi uma aplicação web com Python, Django 5, SQLite e Bootstrap 5 para organizar os atendimentos.”

## 2. Demonstrar o sistema (3 minutos)
1. Faça login com seu usuário de administrador.
2. Mostre o painel com contadores, agenda do dia e próximos atendimentos.
3. Abra Consultas e filtre por profissional e status.
4. Cadastre um paciente fictício em Pacientes.
5. Crie uma consulta futura, das 09:00 às 09:30.
6. Tente outra consulta para o mesmo profissional, das 09:15 às 09:45: mostre a mensagem de conflito.
7. Abra os detalhes e edite o status para Confirmada.
8. Edite para Cancelada e explique que o histórico é preservado.
9. Crie uma consulta descartável, abra Excluir, mostre a confirmação e exclua.
10. Abra `/admin/` e mostre filtros e cadastro de profissionais.

Escolha horários realmente livres no banco e uma data futura antes da apresentação.

## 3. Explicar o código (2 minutos)

| Requisito | Onde mostrar | Explicação simples |
|---|---|---|
| Projeto Django | config/settings.py | Configura o banco, os apps, o idioma e o fuso. |
| Modelos/ORM | consultas/models.py | As classes representam as tabelas; cada consulta se relaciona com paciente e profissional. |
| SQLite | db.sqlite3 e migrations/ | Banco em arquivo e histórico da estrutura. |
| Formulários | consultas/forms.py | ModelForm gera os campos a partir do modelo e valida a entrada. |
| Views | consultas/views.py | Recebem pedidos, consultam o ORM e devolvem páginas. |
| URLs | consultas/urls.py | Ligam cada endereço à sua view. |
| Templates | templates/base.html | A base compartilha menu e estrutura entre as páginas. |
| Bootstrap | static/vendor/ | Fornece componentes e grade; o CSS próprio personaliza o visual. |
| Django Admin | consultas/admin.py | Registra os modelos e configura busca, filtros e colunas. |
| Regras/testes | models.py e tests.py | Evitam conflitos e verificam os fluxos principais. |

Fluxo de uma requisição: navegador → URL → view → formulário/modelo → SQLite → template → navegador.

## 4. Perguntas possíveis

**O que é CRUD?** Create, Read, Update e Delete: cadastrar, consultar, editar e excluir.

**O que é ORM?** Uma camada que permite consultar e modificar o banco usando classes e métodos Python.

**Qual a diferença entre GET e POST?** GET consulta páginas e filtros. POST é usado para salvar, excluir e sair da conta. As operações de escrita usam token CSRF.

**Por que ForeignKey?** Uma consulta pertence a um paciente e a um profissional, que podem ter várias consultas.

**Por que usar PROTECT?** Para impedir a exclusão de um paciente/profissional ainda vinculado a consultas.

**Como detecta conflito?** Há sobreposição quando o início existente é menor que o término novo e o término existente é maior que o início novo, na mesma data e para a mesma pessoa. Consultas canceladas são desconsideradas.

**O que é uma migration?** Um arquivo versionado que descreve alterações na estrutura do banco.

**Como o formulário de edição funciona?** O mesmo ModelForm recebe `instance=consulta`, carregando e atualizando o registro existente.

**Os dados são reais?** Não. Todos os registros enviados são fictícios e servem para apresentação.

## Antes de entregar

- Preencha os dados de identificação abaixo.
- Rode o projeto na sua máquina e pratique o fluxo.
- Leia models.py, forms.py e views.py para conseguir explicar suas decisões.
- Confira as regras do professor sobre apoio de ferramentas e adapte o código ao que estudou.

Aluno(a): ____________________
Turma: _______________________
Professor(a): _________________
Data: ________________________
