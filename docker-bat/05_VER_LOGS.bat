@echo off
title FALAE - Logs Docker

cd /d "%~dp0.."

echo.
echo ==========================================
echo          LOGS DO FALAE
echo ==========================================
echo.
echo Pressione CTRL + C para sair dos logs.
echo Isso nao ira parar os containers.
echo.

docker compose logs -f

echo.
pause