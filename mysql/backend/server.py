from __future__ import print_function
import mysql.connector
from mysql.connector import errorcode
import os
from flask import Flask, request
from flask_limiter import Limiter, util
from hashlib import sha256
import random
import string
import time
import json
import datetime 
app = Flask(__name__)

# connect db
def connect_db():
    cnx = mysql.connector.connect(host='mysqlcontainer', user='root', password='my-secret-pw', port='3306')
    cursor = cnx.cursor()
    return cnx, cursor

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

def use_database(cnx, cursor, DB_NAME):
    try:
        cursor.execute("USE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(DB_NAME))
            cnx.database = DB_NAME
        else:
            print(err)
            exit(1)

def create_table(cnx, cursor, TABLES):
    for table_name in TABLES:
        table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")



def random_name(len=6):
    return ''.join((random.choice(string.ascii_lowercase) for x in range(len)))

def random_pass(len=6):
    return ''.join(str(random.randint(0, 9)) for i in range(len))

def init_user(cnx, cursor, add_user, num=1000000):
    usernames = set([])
    users = []
    cursor.execute(f"SELECT COUNT(*) FROM users")
    number = cursor.fetchone()
    # print(number)
    if number == (1000000,):
        return {'result' : 'Failed'} 
    else:
        while(len(usernames) < num):
            username = random_name(6)
            usernames.add(username)
            

        for username in usernames:
            password = sha256(random_pass(6).encode('utf-8')).hexdigest() 
            users.append((username, password))

        # Disable autocommit
        cnx.autocommit = False
        l = len(users)
        batch_size = l//10
        start_time = time.time()
        for i in range(0, l, batch_size):
            batch = users[i:i + batch_size]
            cursor.executemany(add_user, batch)
            cnx.commit()
        end_time = time.time()

        res = f"Total insertion time: {end_time - start_time} seconds"

        # Re-enable autocommit
        cnx.autocommit = True
        return {'result': 'success'}

def login(cnx, cursor, username, password):
    # print(username + ' ' + password)
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
    data = cursor.fetchone()
    # print(data)
    if data == None:
        return {"result": "failed"}
    else:
        userId, username, passwor,  loggedIn, loggedAt = data
        password_hash = sha256(password.encode()).hexdigest()
        if password_hash != passwor:
            return {"result": "failed"}
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # update state
    cursor.execute("UPDATE users SET loggedIn = 1, loggedAt = %s WHERE username = %s ", (now, username))
    cnx.commit()

    return {"result": "success", "user_id": userId}

def gess_pass(cnx, cursor, username, hashed_arr):
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
    data = cursor.fetchone()
    if data == None:
        return {"result": "No user"}
    else:
        userId, username, passwor, loggedIn, loggedAt = data
        password = str(hashed_arr.index(passwor)).rjust(6, '0')
    return {"result": 'success', "password": password}

def get_all_user(cnx, cursor):
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return {'users': users}

limiter = Limiter( key_func=util.get_remote_address, app=app, default_limits= ["5 per second"])

@app.route('/')
@limiter.limit('5 per minute')
def hello():
    return 'hehe'

@app.route('/init')
@limiter.limit('5 per minute')
def init():
    cnx, cursor = connect_db()
    use_database(cnx, cursor, DB_NAME)
    create_table(cnx, cursor, TABLES)
    res = init_user(cnx, cursor, add_user, num)
    cursor.close()
    cnx.close()
    return res

# @limiter.limit('5 per minute')
# @app.route('/all', methods=['GET'])
# def get_all():
#     cnx, cursor = connect_db()
#     return get_all_user(cnx, cursor)

@app.route("/login", methods=["POST"])
@limiter.limit('5 per second')
def log():
    cnx, cursor = connect_db()
    use_database(cnx, cursor, DB_NAME)
    create_table(cnx, cursor, TABLES)
    res = login(cnx, cursor, request.get_json()["username"], request.get_json()["password"])
    cursor.close()
    cnx.close()
    return res


@app.route('/gess_pass', methods=['POST'])
@limiter.limit('5 per minute')
def gess():
    cnx, cursor = connect_db()
    use_database(cnx, cursor, DB_NAME)
    create_table(cnx, cursor, TABLES)
    res = gess_pass(cnx, cursor, request.get_json()["username"], hashed_arr)
    cursor.close()
    cnx.close()
    return res

if __name__ == '__main__':
    DB_NAME = 'hehe'

    TABLES = {}
    TABLES['users'] = (
        "CREATE TABLE `users` ("
        "  `userId` int(11) NOT NULL AUTO_INCREMENT,"
        "  `username` VARCHAR(256) UNIQUE NOT NULL,"
        "  `password` VARCHAR(256) NOT NULL,"
        "  `loggedIn` TINYINT DEFAULT 0,"
        "  `loggedAt` DATETIME DEFAULT NULL,"
        "  PRIMARY KEY (`userId`)"
        ") ENGINE=InnoDB")
    num = 1000000
    add_user = ("INSERT INTO users "
                "(username, password) "
                "VALUES ( %s, %s)")
    
    hashed_arr = []
    for i in range(1000000):
        str_i = str(i).rjust(6, '0')
        hashed_arr.append(sha256(str_i.encode('utf-8')).hexdigest())

    app.run(host='0.0.0.0',port=5000, debug=True)
    

    