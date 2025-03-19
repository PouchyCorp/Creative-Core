#Projet : Creative Core
#Equipe : Paul Baumard, Abel Bossard, Tybalt Debruyne, Taddeo Boisseuil-Marcil

import pickle, socket
from hashlib import sha256

def send_query( query : str,read : bool, query_parameters : tuple = ()):
        """Send a SQL query to the server and receive the result."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.connect(('127.0.0.1', 5000)) # Connect to the server
        except ConnectionRefusedError:
            print('Connection refused.')
            return
        
        print('Connected, sending query.')

        server.send(pickle.dumps((query, read, query_parameters))) # Send the query to the server
        response = server.recv(4096) #if not a read, response is None

        server.close()
        return pickle.loads(response)
    
def fetch_all_user_data():
    result = send_query('SELECT username, pickled_data FROM users', read=True)

    result = [(row[0], pickle.loads(row[1])) for row in result]

    return result


def hash_password(password : str):
    return sha256(password.encode()).hexdigest()

def fetch_user_data( username):
    result = send_query('SELECT pickled_data FROM users WHERE username == ?', read=True, query_parameters=(username,))

    if result and result[0]:
        pickled_data = result[0][0]
        user_data = pickle.loads(pickled_data)  # Deserialize the data
        print("got user data")
        if type(user_data) is dict:
            return user_data
    
    print("No pickled data found for user, loading default save.")
    return 'default save'

def register_user():
    username = 'test'
    password = 'test'

    pickled_data = pickle.dumps('default_save')  # Serialize the default save data to send to the database
    send_query('INSERT INTO users (username, password, pickled_data) VALUES (?, ?, ?)', read=False, query_parameters=(username, hash_password(password), pickled_data))



def login_user():
    username = 'test'
    password = 'test'
    
    result = send_query('SELECT password FROM users WHERE username = ?', read=True, query_parameters=(username,))

    if hash_password(password) == result[0]:
        print('Login successful')
        return True

def save_user_data( username, data : dict):
    """
    Save pickled user data to the database.
    Args:
        username (str): The username of the user.
        data (dict): The data to be pickled and saved.
    """
    pickled_data = pickle.dumps(data)  # Serialize the data

    send_query('UPDATE users SET pickled_data = ? WHERE username = ?', read=False, query_parameters=(pickled_data, username))

    print('successfuly saved')

#tests
if __name__ == '__main__':
    register_user()
    login_user()
    fetch_user_data('test')
    save_user_data('test', {'test': 'test'})
