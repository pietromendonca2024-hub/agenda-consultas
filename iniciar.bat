@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
    echo Instale Python 3.10 ou superior com o Python Launcher.
    echo Depois execute este arquivo novamente.
    pause
    exit /b 1
)
if not exist .venv\Scripts\python.exe (
    py -3 -m venv .venv
    if errorlevel 1 goto erro
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto erro
.venv\Scripts\python.exe manage.py migrate
if errorlevel 1 goto erro
.venv\Scripts\python.exe manage.py popular_demo
if errorlevel 1 goto erro
.venv\Scripts\python.exe manage.py shell -c "from django.contrib.auth import get_user_model; raise SystemExit(0 if get_user_model().objects.filter(is_superuser=True).exists() else 1)"
if errorlevel 1 (
    echo.
    echo PRIMEIRO ACESSO: escolha seu usuario e sua senha.
    echo A senha nao aparece enquanto voce digita. Isso e normal.
    .venv\Scripts\python.exe manage.py createsuperuser
    if errorlevel 1 goto erro
)
echo.
echo Abra no navegador: http://127.0.0.1:8000/
echo Para encerrar, pressione Ctrl+C nesta janela.
.venv\Scripts\python.exe manage.py runserver
pause
exit /b 0
:erro
echo.
echo Nao foi possivel iniciar. Confira a mensagem acima.
pause
exit /b 1
