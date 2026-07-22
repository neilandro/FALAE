@echo off
title FALAE - Reconstruir Docker

cd /d "%~dp0.."

echo.
echo ==========================================
echo      RECONSTRUINDO O FALAE NO DOCKER
echo ==========================================
echo.
echo Esse processo ira reconstruir as imagens
echo e recriar os containers.
echo.
echo Os volumes do banco NAO serao apagados.
echo.

docker compose down

if errorlevel 1 (
    echo.
    echo [ERRO] Nao foi possivel encerrar os containers.
    echo.
    pause
    exit /b 1
)

docker compose build

if errorlevel 1 (
    echo.
    echo [ERRO] A construcao das imagens falhou.
    echo.
    pause
    exit /b 1
)

docker compose up -d

if errorlevel 1 (
    echo.
    echo [ERRO] As imagens foram construidas,
    echo mas os containers nao iniciaram.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] FALAE reconstruido e iniciado com sucesso.
echo.

docker compose ps

echo.
pause