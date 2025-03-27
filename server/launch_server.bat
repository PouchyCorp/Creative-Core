@echo off

:: create a virtual environment
echo Creation de l'environnement virtuel...
python -m venv server_venv

:: Set default values
set "defaultIP=127.0.0.1"
set "defaultPort=5000"

:: Prompt for IP
set /p "serverIP=Entrez ip du serveur (Par defaut: %defaultIP%): "
if "%serverIP%"=="" set "serverIP=%defaultIP%"

:: Prompt for Port
set /p "serverPort=Entrez port du serveur (Par defaut: %defaultPort%): "
if "%serverPort%"=="" set "serverPort=%defaultPort%"

:: launch the game
echo Credits : PouchyCorp (Paul), Tioh (Tadd), Ytyt (Tyb), Leih (Abl)
echo Lancement du serveur ...
server_venv\Scripts\python.exe database_server.py %serverIP% %serverPort%
