from __future__ import print_function
import mysql.connector
from mysql.connector import errorcode

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
    cnx = mysql.connector.connect(user='root', password='QuocAnh24102001')
    cursor = cnx.cursor()
    return cnx, cursor

def create_db(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

def create_database(cnx, cursor, DB_NAME):
    try:
        cursor.execute("USE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_db(cursor)
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
    while(len(usernames) < num):
        username = random_name(6)
        usernames.add(username)
        

    for username in usernames:
        passw = random_pass(6)
        password = sha256(passw.encode('utf-8')).hexdigest() 
        users.append((username, password, passw))

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

    print("Total insertion time:", end_time - start_time, "seconds")

    # Re-enable autocommit
    cnx.autocommit = True

def login(cnx, cursor, username, password):
    # print(username + ' ' + password)
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
    data = cursor.fetchone()
    print(data)
    if data == None:
        return json.dumps({"result": "failed"})
    else:
        userId, username, passwor, passw, loggedIn, loggedAt = data
        password_hash = sha256(password.encode()).hexdigest()
        if password_hash != passwor:
            return json.dumps({"result": "failed"})
    now = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    # update state
    cursor.execute("UPDATE users SET loggedIn = 1, loggedAt = %s WHERE username = %s ", (now, username))
    cnx.commit()

    return json.dumps({"result": "success", "user_id": userId})

def gess_pass(cnx, cursor, username):
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
    data = cursor.fetchone()
    if data == None:
        return json.dumps({"result": "failed"})
    else:
        userId, username, passwor, passw, loggedIn, loggedAt = data
        # password_hash = sha256(password.encode()).hexdigest()
    return passw

def get_all_user(cnx, cursor):
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return json.dumps({'users': users})

limiter = Limiter(util.get_remote_address, app=app, default_limits= ["5 per second"])

@limiter.limit('5 per second')
@app.route('/')
def hello():
    return 'hehe'

@limiter.limit('5 per second')
@app.route('/all', methods=['GET'])
def get_all():
    return get_all_user(cnx, cursor)

@limiter.limit('5 per second')
@app.route("/login", methods=["POST"])
def log():
    return login(cnx, cursor, request.get_json()["username"], request.get_json()["password"])

@limiter.limit('5 per minutes', override_defaults=True)
@app.route('/gess_pass', methods=['POST'])
def gess():
    return gess_pass(cnx, cursor, request.get_json()["username"])

if __name__ == '__main__':
    DB_NAME = 'hehe'

    TABLES = {}
    TABLES['users'] = (
        "CREATE TABLE `users` ("
        "  `userId` int(11) NOT NULL AUTO_INCREMENT,"
        "  `username` VARCHAR(256) UNIQUE NOT NULL,"
        "  `password` VARCHAR(256) NOT NULL,"
        "  `passw` VARCHAR(256) NOT NULL,"
        "  `loggedIn` TINYINT DEFAULT 0,"
        "  `loggedAt` DATETIME DEFAULT NULL,"
        "  PRIMARY KEY (`userId`)"
        ") ENGINE=InnoDB")
    num = 1000000
    add_user = ("INSERT INTO users "
                "(username, password, passw) "
                "VALUES ( %s, %s, %s)")
    cnx, cursor = connect_db()
    create_database(cnx, cursor, DB_NAME)
    create_table(cnx, cursor, TABLES)
    # init_user(cnx, cursor, add_user, num)
    app.run(host='0.0.0.0', port=2410)
    
# cursor.close()
# cnx.close()