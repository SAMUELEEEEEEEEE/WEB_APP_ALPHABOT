#Authors: Meinero Samuele, Menardi Samuele
#Classe 5AROB

#Importazione delle librerie necessarie al funzionamento del codice
from flask import Flask, render_template, redirect, url_for, request, make_response
import AlphaBot
import sqlite3 as sql
import time
import random
import string
import hashlib
import datetime

#Oggetto della classe Flask
app = Flask(__name__)

#Istanza della classe alphabot
alpha = AlphaBot.AlphaBot()

def generatore_token():
    """
    Funzione per generare un token casuale per l'autenticazione
    """
    #Caratteri utilizzabili nella generazione
    characters = string.ascii_letters + string.digits

    # Genera una stringa alfanumerica casuale di 40 caratteri
    alphaNumeric_string = ''.join(random.choice(characters) for _ in range(40))

    return alphaNumeric_string

token_advanced = generatore_token()  # Genera un token casuale per l'autenticazione della pagina advanced
token_based = generatore_token()  # Genera un token casuale per l'autenticazione della pagina based

# Funzione per validare le credenziali di accesso
def validate(username, password):
    completion = False
    con = sql.connect('./db.db')  # Connessione al database
    cur = con.cursor()
    cur.execute("SELECT * FROM Users")  # Recupera tutti gli utenti dal database
    rows = cur.fetchall()

    #Chiusura cursore e connessione
    cur.close()
    con.close()

    for row in rows:
        dbUser = row[1]
        dbPass = row[2]
        if dbUser == username:
            completion = check_password(dbPass, password)
    return completion

def encode_hash(string):
    """
    Funzione per generare l'hash di una stringa usando l'algoritmo SHA-256
    """
    sha256 = hashlib.sha256()
    sha256.update(string.encode('utf-8'))
    hash_result = sha256.hexdigest()
    return hash_result

def check_password(hashed_password, user_password):
    """
    Funzione per verificare se una password coincide con l'hash nel database
    """
    return hashed_password == encode_hash(user_password)

# Funzione decoratore dell'app Flask
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        completion = validate(username, password)
        if completion == False:
            error = 'Credenziali non valide. Riprova.'
        else:
            #Se le password sono corrette gestisce il cookie
            user_cookie = request.cookies.get('username')
            print(user_cookie)
            if user_cookie is None:
                #Settare il cookie se e' assente
                if username == "samuele":
                    resp = make_response(redirect(url_for('index_advanced')))
                    resp.set_cookie('username', 'samuele')
                    
                    return resp
                else:
                    resp = make_response(redirect(url_for('index_based')))
                    resp.set_cookie('username', f'{username}')
                    return resp
            else:
                #Reindirizzare nella pagina giusta
                if username == "samuele":
                    resp = make_response(redirect(url_for('index_advanced')))
                    resp.set_cookie('username', 'samuele')
                    return resp
                else:
                    resp = make_response(redirect(url_for('index_based')))
                    resp.set_cookie('username', f'{username}')
                    return resp
            #return redirect(url_for('index'))
    elif request.method == 'GET':
        return render_template('login.html', error=error)

    return render_template('login.html', error=error)

# Indicizza i comandi e le relative azioni associate
COMMAND = ["RS", "SQ", "TA"]
commandDict = {"B": alpha.backward, "F": alpha.forward, "L": alpha.left, "R": alpha.right, "S": alpha.stop}

# Funzione per interrogare il database ed eseguire una sequenza di movimenti associata a una shortcut
def db_interrogation(sh):

    #print(sh)

    conn = sql.connect("./movements.db") #Connessione al db
    cursor = conn.cursor()

    cursor.execute(f"SELECT Mov_sequence FROM Movements WHERE Shortcut = '{sh}'")

    res = cursor.fetchall()

    #Chisura del cursore e della connessione
    cursor.close()
    conn.close()

    for command in res[0][0].split("-"):
        commandDict[command.split(";")[0]]()  # Esegue il comando di movimento
        time.sleep(float(command.split(";")[1]))
        alpha.stop()
        print(command)

# Funzione decoratore per gestire la pagina principale avanzata
@app.route(f"/{token_advanced}", methods=['GET', 'POST'])
def index_advanced():
    if request.method == 'POST':
        #A seconda del comando inserito -> esegue un movimento
        if request.form.get('F') == 'Forward':
            #print(">>Forward")
            alpha.forward()
            movement = 'forward'

        elif request.form.get('B') == 'Backward':
            #print(">>Backward")
            alpha.backward()
            movement = 'backward'

        elif request.form.get('S') == 'Stop':
            #print(">>Stop")
            alpha.stop()
            movement = 'stop'

        elif request.form.get('R') == 'Right':
            #print(">>Right")
            alpha.right()
            movement = 'right'

        elif request.form.get('L') == 'Left':
            #print(">>Left")
            alpha.left()
            movement = 'left'

        #Per i comandi "speciali" interroga il db
        elif request.form.get("rs") == "RS":
            db_interrogation("RS")
            movement = 'reverse'

        elif request.form.get("ta") == "TA":
            db_interrogation("TA")
            movement = 'turn around'

        elif request.form.get("sq") == "SQ":
            db_interrogation("SQ")
            movement = 'square'

        else:
            print("Unknown")

        timeDate = datetime.datetime.now()
        user = request.cookies.get('username')

        #Connessione al db
        db_connection = sql.connect("db.db")
        cursor_connection = db_connection.cursor()
        
        cursor_connection.execute(f"INSERT INTO History VALUES ('{user}', '{timeDate}', '{movement}')")
        print(f"INSERT INTO History VALUES ('{user}', '{timeDate}', '{movement}')")
        #Chiusura al db
        cursor_connection.close()

        db_connection.commit()

        db_connection.close()

    elif request.method == 'GET':
        resp = make_response(render_template('index_advanced.html'))
        resp.set_cookie('username', 'samuele')
        return resp

    return render_template("index_advanced.html")

# Funzione decoratore per gestire la pagina principale di base
@app.route(f"/{token_based}", methods=['GET', 'POST'])
def index_based():

    if request.method == 'POST':
        #A seconda del comando inserito -> esegue un movimento
        if request.form.get('F') == 'Forward':
            #print(">>Forward")
            alpha.forward()
            movement = 'forward'

        elif request.form.get('B') == 'Backward':
            #print(">>Backward")
            alpha.backward()
            movement = 'backward'

        elif request.form.get('S') == 'Stop':
            #print(">>Stop")
            alpha.stop()
            movement = 'stop'

        elif request.form.get('R') == 'Right':
            #print(">>Right")
            alpha.right()
            movement = 'right'

        elif request.form.get('L') == 'Left':
            #print(">>Left")
            alpha.left()
            movement = 'left'

        else:
            print("Unknown")

        timeDate = datetime.datetime.now()
        user = request.cookies.get('username')

        #Connessione al db
        db_connection = sql.connect("db.db")
        cursor_connection = db_connection.cursor()
        
        cursor_connection.execute(f"INSERT INTO History VALUES ('{user}', '{timeDate}', '{movement}')")
        print(f"INSERT INTO History VALUES ('{user}', '{timeDate}', '{movement}')")

        #Chiusura al db
        cursor_connection.close()

        db_connection.commit()

        db_connection.close()

    elif request.method == 'GET':
        resp = make_response(render_template('index_based.html'))
        resp.set_cookie('username', request.cookies.get('username'))
        return resp

    return render_template("index_based.html")

# Esegue l'app Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
