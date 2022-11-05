import os
import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
            host='database',
            database=os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'])
    return conn

def change_crypto_price(symbol: str, amount: int):
    """This function changes the cryptocurrency price with a custom amount

    Args:
        symbol (str): Symbol of cryptocurrency
        amount (int): Amount of change. Can be negative.
    """

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT * FROM crypto WHERE symbol = %s;', [symbol])
        result = cur.fetchone()
        newvalue = result[3] + amount
        if result:
            cur.execute('UPDATE crypto SET price = %s WHERE id = %s;', [newvalue, result[0]])
    except psycopg2.Error as e:
        print(e)
        
    conn.commit()
    cur.close()
    conn.close()

def add_price_100(symbol: str):
    """This function adds 100 to the cryptocurrency price

    Args:
        symbol (str): Symbol of cryptocurrency
    """
    change_crypto_price(symbol, 100)

def sub_price_100(symbol: str):
    """This function subs 100 from the cryptocurrency price

    Args:
        symbol (str): Symbol of cryptocurrency
    """
    change_crypto_price(symbol, -100)