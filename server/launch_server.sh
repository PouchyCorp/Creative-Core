#!/bin/bash

# Create a virtual environment
echo "Creation de l'environnement virtuel..."
python3 -m venv server_venv

# Set default values
defaultIP="127.0.0.1"
defaultPort="5000"

# Prompt for IP
read -p "Entrez ip du serveur (Par defaut: $defaultIP): " serverIP
if [ -z "$serverIP" ]; then
  serverIP=$defaultIP
fi

# Prompt for Port
read -p "Entrez port du serveur (Par defaut: $defaultPort): " serverPort
if [ -z "$serverPort" ]; then
  serverPort=$defaultPort
fi

# Launch the game
echo "Credits : PouchyCorp (Paul), Tioh (Tadd), Ytyt (Tyb), Leih (Abl)"
echo "Lancement du serveur ..."
server_venv/bin/python3 database_server.py "$serverIP" "$serverPort"
