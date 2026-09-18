# Validação da entrega

- Ambiente de verificação: Python 3.12, Django 5.2.17, SQLite e Chromium em Linux.
- `python manage.py check`: nenhum problema identificado.
- `python manage.py makemigrations --check --dry-run`: nenhuma alteração pendente.
- `python manage.py test`: **24 testes aprovados**.
- Testes cobrem CRUD, conflitos entre intervalos, horários adjacentes, cancelamento, validação pelo Admin, filtros, paginação, autenticação, acesso restrito, CSRF, dados de pacientes, proteção de relacionamentos e carga demonstrativa sem duplicação.
- Login e navegação real conferidos no Chromium; recursos CSS/JS carregados localmente, sem erros HTTP/JavaScript nas páginas percorridas.
- Capturas em 1440 px e 390 px de largura, em `docs/telas/`.
- Painel e formulário revisados em 390 px, sem transbordamento horizontal da página. Tabelas e menu usam rolagem própria quando necessário.
- Banco final: 16 consultas fictícias, 12 pacientes e 4 profissionais. Conta temporária de revisão e sessões removidas.

O inicializador `.bat` foi escrito para Windows, mas não foi executado em Windows neste ambiente. Os comandos Django que ele utiliza foram executados em Linux. O projeto não foi publicado como serviço de produção.
