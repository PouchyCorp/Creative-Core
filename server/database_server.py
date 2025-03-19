r"""
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
   _____            _                            _             _       _        _                    
  / ____|          | |                          | |           | |     | |      | |                   
 | |     ___   ___ | |  _ __ ___ _ __ ___   ___ | |_ ___    __| | __ _| |_ __ _| |__   __ _ ___  ___ 
 | |    / _ \ / _ \| | | '__/ _ \ '_ ` _ \ / _ \| __/ _ \  / _` |/ _` | __/ _` | '_ \ / _` / __|/ _ \
 | |___| (_) | (_) | | | | |  __/ | | | | | (_) | ||  __/ | (_| | (_| | || (_| | |_) | (_| \__ \  __/
  \_____\___/ \___/|_| |_|  \___|_| |_| |_|\___/ \__\___|  \__,_|\__,_|\__\__,_|_.__/ \__,_|___/\___|
                                                                                                     
Basic SQLite query server that listens for incoming connections from clients and executes the queries they send.                                                                                     

Note:
----
I should implement error handling if I have the courage to do so.
This server is vulnerable to SQL injection attacks, the queries are executed 'as is', so don't connect it to the internet.

For more information on how the server / client communication works, see the /docs/detail_implementation.mb

Author : Ytyt (Tybalt)
"""

import socket
import sqlite3
import threading
import pickle
import sys

CHUNK_SIZE = 4096 # The size of the chunks to receive from the client (this should be consistent with the client's CHUNK_SIZE)

# Database setup
DB_NAME = "user_data.db"
HOST_IP = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

def initialize_database():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            pickled_data BLOB)
    ''')
    connection.commit()
    connection.close()
    print("Base de donnée initialisée :)")

def execute_query(query: str, read: bool, query_parameters: tuple = ()):
    """Execute a SQL query on the return the result if read is True."""
    error_status = "!OK!"
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute(query, query_parameters)

    except sqlite3.IntegrityError:
        error_status = "!INTEGR!"

    if read:  # If the query is a SELECT query, return the result
        result = cursor.fetchall()
    else:  # If the query is an INSERT, UPDATE or DELETE query, commit the changes
        conn.commit()
        result = None
    print(f"Requete executée : {query}")
    conn.close()

    return (error_status, result)

def handle_client(client_socket: socket.socket):
    """
    Handle communication with a client.
    Read the client's documention for more information (same inner workings, just in reverse).
    """
    while True:
        # Receive the length of the serialized data first
        try:
            data_length = int.from_bytes(client_socket.recv(4), byteorder='big')
        except Exception as e:
            print(e)
            break
        
        # Receive the serialized data in chunks
        data = bytearray()
        while len(data) < data_length:
            chunk = client_socket.recv(CHUNK_SIZE)
            if not chunk: # If the client closes the connection, break the loop
                break
            data.extend(chunk)

        if not data:
            break

        query, read, query_parameters = pickle.loads(data)
        error_status, response = execute_query(query, read, tuple(query_parameters))

        client_socket.send(error_status.encode())
        # Serialize the response
        serialized_response = pickle.dumps(response)

        # Send the length of the serialized response first
        client_socket.sendall(len(serialized_response).to_bytes(4, byteorder='big'))

        # Send the serialized response in chunks
        for i in range(0, len(serialized_response), CHUNK_SIZE):
            client_socket.sendall(serialized_response[i:i + CHUNK_SIZE])

    client_socket.close()
    print("Connection fermée avec un client")

def start_server(host_ip, port):
    """Start the SQLite query server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host_ip, port))
    server.listen()
    print(f"Le serveur écoute en {host_ip} avec sur le port : {port}")
    while True:  # Accept connections from clients
        client_socket, addr = server.accept()
        print(f"Connection établie avec {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))  # Handle each client in a separate thread
        client_thread.start()

if __name__ == "__main__":
    initialize_database()
    start_server(HOST_IP, PORT)