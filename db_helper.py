# -*- coding: utf-8 -*-
import sqlite3
import datetime

def execute_q(query,data=""):
    try:
        con = sqlite3.connect("naelo.db")
        cur = con.cursor()
    except sqlite3.Error as err:
        print (err.args)
        return 1
    try:
        r = cur.execute(query,data)
    except sqlite3.Error as err:
        print ("DB error: "+err.args[0])
        print ("Query:" + query + " ; " +str(data))
        con.close()
        return 1
    #if data != None:
    data = r.fetchall()
    con.commit()
    con.close()
    return data


def create_db():
    query = ('CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
             'name TEXT NOT NULL, matrix_name TEXT, points INTEGER NOT NULL,'
             'created_by TEXT, created_at TEXT);')
    execute_q(query)

    query = ('CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
             'white_id INTEGER NOT NULL, black_id INTEGER NOT NULL, result REAL NOT NULL,'
             'comment TEXT, date TEXT NOT NULL, creator_id INTEGER NOT NULL);')
    execute_q(query)


def create_player(name,aliases="",creator=None):
    dt = datetime.datetime.now()

    if player_exists(name): #TODO or in aliases
        return False
    if aliases != "":
        query = 'INSERT INTO players(name,points,created_at,aliases) VALUES(?,1500,?,?);'
        execute_q(query,(name,dt,aliases))
    else:
        query = 'INSERT INTO players(name,points,created_at) VALUES(?,1500,?);'
        execute_q(query,(name,dt))

    return True


def player_exists(player):
    query = 'SELECT name, aliases from players;'
    players = execute_q(query)
    #print (players)
    #TODO search aliasies! AP:sql?
    if player in [j for i in players for j in i]:
        return True
    else:
        return False


def check_add_game(white,black,result,creator):
    #TODO check if players exists and if wants to validate

    if player_exists(white) and player_exists(black):
    #TODO ...if good:
        return add_game(white,black,result,creator)
    else:
        return "fehler bei check_add_game()"


def calc_elo(w_elo,b_elo,result):
    #Erwartungswert Weiss:
    EW = 1/ (1 + 10**((b_elo-w_elo)/400))
    EB = 1/ (1 + 10**((w_elo-b_elo)/400))
    #Anpassung der Elo-Zahl:
    k = 36 #const factor
    elo_change =  k *(result-EW)
    #TODO...
    return elo_change

    #TODO make sure game is valid and verified.
def add_game(white,black,result,creator):
    #Get creator:
    #query = ('SELECT id FROM players WHERE name = \"{}\"'.format(creator))
    #creator_id = execute_q(query)[0][0]
    #DEBUG: =1 until db stores Matrix Names and creator can match:
    creator_id=1

    dt = datetime.datetime.now() #TODO  datetime sollte bei checkgame gemerkt werden und hier übernommen. -> DB
    #get Players Points from db
    query = 'SELECT id, points FROM players WHERE name = ?;'
    w_id, w_elo = execute_q(query,(white,))[0]
    b_id, b_elo = execute_q(query,(black,))[0]


    #Add Game
    query = ('INSERT INTO games(white_id,black_id,result,date,creator_id) VALUES(?,?,?,?,?);')
    execute_q(query,(w_id,b_id,result,dt,creator_id))
    #TODO improve result eval

    #Erwartungswert Weiss:
    EW = 1/ (1 + 10**((b_elo-w_elo)/400))
    EB = 1/ (1 + 10**((w_elo-b_elo)/400))
    #Anpassung der Elo-Zahl:
    k = 36 #const factor

    w_elo_change =  k *(result-EW)
    new_w_elo = w_elo + w_elo_change#Neue Elo für weiß
    #Eintragen:
    update_elo(w_id,round(new_w_elo))

    #Turn result for black TODO: better solution
    if result == 0:
        result = 1
    elif result == 1:
        result = 0

    b_elo_change = k *(result-EB)
    new_b_elo = b_elo + b_elo_change # neue Elo für schwarz
    update_elo(b_id,round(new_b_elo))
    #w_elo = execute_q("SELECT )
    #calc new elo
    return ("Punkte Änderung weiß: {0}  schwarz: {1}".format(round(w_elo_change),round(b_elo_change)))


def update_elo(player_id,points):
    query = 'UPDATE players SET points = ? WHERE id = ?;'
    execute_q(query,(points,player_id))


def get_elolist():
    query = "SELECT name,points from players;"
    result = execute_q(query)
    result.sort(key=lambda t:t[1],reverse=True)
    text = "Wertung\n\n"
    i=1
    for e in result:
        text +=  "{0}. {1}  -  {2} Punkte\n".format(i,e[0],e[1])
        i+=1
    #TODO Make HTML table
    return text


def get_games(number=5,player=None):
    query='SELECT white_id,black_id,result,date,id from games ORDER BY date DESC LIMIT ?'
    games = execute_q(query,(number,))
    players = execute_q("SELECT id,name from players")
    players = {a:b for a,b in players}
    result = ""
    for g in games:
        w = players[g[0]]
        b = players[g[1]]
        g_result = g[2]
        date = g[3][:16]
        g_id = g[4]
        date = datetime.datetime.strptime(date,"%Y-%m-%d %H:%M")
        date = date.strftime("%d.%m.%Y - %H:%M")
        result += ('{0} gegen {1}   Ergebnis: {2} am {3} Uhr  [{4}]\n'.format(w,b,g_result,date,g_id))

    #playerid to name
    return result


def tests():
    pass



