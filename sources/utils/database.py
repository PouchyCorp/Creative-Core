r""" 
Projet : Creative Core
Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil
  _____        _        _                                    
 |  __ \      | |      | |                                   
 | |  | | __ _| |_ __ _| |__   __ _ ___  ___                 
 | |  | |/ _` | __/ _` | '_ \ / _` / __|/ _ \                
 | |__| | (_| | || (_| | |_) | (_| \__ \  __/                
 |_____/ \__,_|\__\__,_|_.__/ \__,_|___/\___|       

Key features:
-------------
- Database class for handling user registration, login, and data storage.
- Hashing of user passwords for security.
- Serialization and deserialization of user data for database storage (with a cool packet system ^^).
- User data getting and saving.

Author: Ytyt (Tybalt), with help from Pouchy for the custom packet system.
"""

import socket, pickle
from hashlib import sha256
from ui.infopopup import InfoPopup
from utils.room_config import DEFAULT_SAVE

class Database:
    def __init__(self, server_ip, server_port, info_popups : list[InfoPopup]):
        self.server_ip = server_ip
        self.server_port = server_port
        self.info_popups = info_popups
        self.chunk_size = 4096

    def send_query(self, query: str, read: bool, query_parameters: tuple = ()):
        """Send a SQL query to the server and receive the result.
        The read parameter indicates whether the query is a SELECT query (to let the server know if he needs to send a response).
        Basic explanation:
            Sending query to the server:
        1 - Serialize the query and parameters
        2 - Send the length of the serialized data first
        3 - Send the serialized data in chunks

            Receiving the result from the server:
        1 - Receive the length of the response first
        2 - Receive the response in chunks
        3 - Assemble the response
        3 - Deserialize the response"""

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.connect((self.server_ip, self.server_port)) # Connect to the server
        except Exception as e:
            raise ConnectionRefusedError(f'ERROR {e}\n Essayez de passer en mode hors-ligne dans config.toml')

        # Serialize the query and parameters
        serialized_query = pickle.dumps((query, read, query_parameters))

        # Send the length of the serialized data first
        server.sendall(len(serialized_query).to_bytes(4, byteorder='big'))

        # Send the serialized data in chunks
        for i in range(0, len(serialized_query), self.chunk_size):
            server.sendall(serialized_query[i:i + self.chunk_size])

        # Eventually recieve exeption encountered by the server (8 character max)
        # "!OK!" means no error
        # "!INTEGR!" means an integrity error (username already exists)
        error_status = server.recv(8).decode()
        if error_status != "!OK!":
            return error_status

        # Receive the length of the response first
        response_length = int.from_bytes(server.recv(4), byteorder='big')

        # Receive the response in chunks
        response = bytearray()
        while len(response) < response_length:
            chunk = server.recv(self.chunk_size)
            if not chunk:
                break
            response.extend(chunk)

        server.close()
        return pickle.loads(response)
    
    def fetch_all_user_data(self):
        result = self.send_query('SELECT username, pickled_data FROM users', read=True)
        

        result = [(row[0], pickle.loads(row[1])) for row in result]

        return result


    def hash_password(self, password : str):
        return sha256(password.encode()).hexdigest()

    def fetch_user_data(self, username):
        result = self.send_query('SELECT pickled_data FROM users WHERE username == ?', read=True, query_parameters=(username,))

        if result and result[0]:
            pickled_data = result[0][0]
            user_data = pickle.loads(pickled_data)  # Deserialize the data
            print("Got user data")
            if type(user_data) is dict:
                return user_data
        
        print("No pickled data found for user, loading default save.")
        return DEFAULT_SAVE

    def register_user(self, username, password):
        
        if not username or not password:
            self.info_popups.append(InfoPopup("Les deux champs sont requis!"))
            return
        
        pickled_data = pickle.dumps(DEFAULT_SAVE)  # Serialize the default save data to send to the database
        error_status = self.send_query('INSERT INTO users (username, password, pickled_data) VALUES (?, ?, ?)', read=False, query_parameters=(username, self.hash_password(password), pickled_data))

        if error_status == '!INTEGR!':
            self.info_popups.append(InfoPopup("Ce nom d'utilisateur est déjà pris."))
        else:
            self.info_popups.append(InfoPopup("Inscription réussie."))
                                    


    def login_user(self, username, password):
        if not username or not password:
            self.info_popups.append(InfoPopup("Les deux champs sont requis!"))
            return False
        
        result = self.send_query('SELECT password FROM users WHERE username = ?', read=True, query_parameters=(username,))
        if result and result[0][0] == self.hash_password(password):
            self.info_popups.append(InfoPopup("Connexion réussie."))
            return True
        else:
            self.info_popups.append(InfoPopup("Nom d'utilisateur ou mot de passe incorrect."))
            return False

    def save_user_data(self, username, data : dict):
        """
        Save pickled user data to the database.
        """
        pickled_data = pickle.dumps(data)  # Serialize the data

        self.send_query('UPDATE users SET pickled_data = ? WHERE username = ?', read=False, query_parameters=(pickled_data, username))

        print(f"{username}'s data successfuly saved !")