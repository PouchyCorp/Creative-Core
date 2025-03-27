#!/bin/bash

# Create a virtual environment
echo "Creating a virtual environment..."
python3 -m venv creative_core_venv

# Install dependencies
echo "Installing dependencies..."
creative_core_venv/bin/pip install --upgrade pip
creative_core_venv/bin/pip install -r requirements.txt

# Launch the game
echo "Launching the game..."
echo "Credits : PouchyCorp, Tioh, Ytyt, Leih"
creative_core_venv/bin/python3 sources/main.py
