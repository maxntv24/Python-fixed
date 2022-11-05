import os
import psycopg2
import random
import string

def generate_verify_code(length: int) -> str:
    """This function generates a random sample verify code

    Args:
        length (int): Length of verify code

    Returns:
        verify_code (str): Generated verify code
    """
    letters = string.ascii_lowercase + string.digits
    verify_code = ''.join(random.choice(letters) for i in range(length))
    return verify_code

def init():
    conn = psycopg2.connect(
            host='database',
            database=os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'])

    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS users;')
    cur.execute('DROP TABLE IF EXISTS verifycode;')
    cur.execute('DROP TABLE IF EXISTS crypto;')

    cur.execute('CREATE TABLE verifycode (id serial PRIMARY KEY,'
                                        'code varchar (32) NOT NULL UNIQUE);')

    cur.execute('INSERT INTO verifycode (code) VALUES (\'{}\');'.format(generate_verify_code(32)))

    cur.execute('CREATE TABLE users (id serial PRIMARY KEY,'
                                    'username varchar (20) NOT NULL UNIQUE,'
                                    'password varchar (50) NOT NULL,'
                                    'fullname varchar (50) NOT NULL,'
                                    'phone varchar (20) NOT NULL,'
                                    'email varchar (50) NOT NULL,'
                                    'token varchar (255) DEFAULT NULL,'
                                    'verifycode serial,'
                                    'CONSTRAINT fk_verifycode FOREIGN KEY(verifycode)' 
                                    'REFERENCES verifycode(id));')


    cur.execute('INSERT INTO users (username, password, fullname, phone, email, verifycode)'
                'VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\');'.format('guest', '084e0343a0486ff05530df6c705c8bb4', 'youtube.com/watch?v=dQw4w9WgXcQ', '00', 'guest@guest.com', 1))
                
    cur.execute('INSERT INTO users (username, password, fullname, phone, email, verifycode)'
                'VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\');'.format('fl4g', '7b94bf8a6cdbfc2cd1ec1180047ce3bb', 'Try to access this user', '11', 'fl4g@mail.co', 1))

    cur.execute('CREATE TABLE crypto (id serial PRIMARY KEY,'
                                    'symbol varchar (5) NOT NULL UNIQUE,'
                                    'name varchar (20) NOT NULL,'
                                    'price int NOT NULL);')

    cur.execute('INSERT INTO crypto (symbol, name, price)'
                'VALUES (\'{}\', \'{}\', \'{}\');'.format('CBJS', 'Cyberjutsu', 1337))

    cur.execute('INSERT INTO crypto (symbol, name, price)'
                'VALUES (\'{}\', \'{}\', \'{}\');'.format('BTC', 'Bitcoin', 1337))

    cur.execute('INSERT INTO crypto (symbol, name, price)'
                'VALUES (\'{}\', \'{}\', \'{}\');'.format('ETH', 'Ethereum', 1337))
    
    cur.execute('INSERT INTO crypto (symbol, name, price)'
                'VALUES (\'{}\', \'{}\', \'{}\');'.format('XRP', 'Ripple', 1337))
    
    cur.execute('INSERT INTO crypto (symbol, name, price)'
                'VALUES (\'{}\', \'{}\', \'{}\');'.format('LTC', 'Litecoin', 1337))
    
    cur.execute('INSERT INTO crypto (symbol, name, price)'
                'VALUES (\'{}\', \'{}\', \'{}\');'.format('XMR', 'Monero', 1337))

    conn.commit()

    cur.close()
    conn.close()

def get_crypto_info():
    conn = psycopg2.connect(
            host='database',
            database=os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'])

    cur = conn.cursor()
    cur.execute('SELECT * FROM crypto;')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data