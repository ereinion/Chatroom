import os
import uuid
import psycopg2
import psycopg2.extras
from flask import Flask, session
import uuid
from flask.ext.socketio import SocketIO, emit
from flask_socketio import join_room, leave_room


app = Flask(__name__, static_url_path='')
socketio = SocketIO(app)
app.config['SECRET_KEY'] = 'secret!'
app.secret_key = os.urandom(24).encode('hex')


messages = [{'text': 'Booting system', 'name': 'Bot'}, {'text': 'ISS Chat now live!', 'name': 'Bot'},]

users = {}

activeroom = ''

def connectToDB():
  connectionString = 'dbname=chat user=chatadmin password=zomboy host=localhost'
 # print connectionString
  try:
    return psycopg2.connect(connectionString)
  except:
    print("Can't connect to database")
    
    
@socketio.on('connect', namespace='/iss')
def connect():
    session['uuid'] = uuid.uuid1()
    session['username'] = 'New User'

    users[session['uuid']] = {'username': 'New user'}
    print('connected!')
    session['activeroom'] = 'room1'
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = cur.mogrify("select name, text, room from chatlog WHERE room = 'room1' ORDER BY id DESC LIMIT 10;")
    cur.execute(query)
    pastmessages = cur.fetchall()
    pastmessagesdict = {}
    pastmessages.reverse()
    for message in pastmessages:
        pastmessagesdict={'text': message[1], 'name' : message[0]}
        #print(pastmessagesdict)
        emit('message', pastmessagesdict)

@socketio.on('disconnect')
def on_disconnect():
    if session['uuid'] in users:
        del users[session['uuid']]
        room=session['activeroom']
        leave_room(room)
        
@socketio.on('login', namespace='/iss')        
def login(un, pw):
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    username = un
    password = pw
    if "'" in username:
        
          username=username.replace("'", "''")
          
    if "'" in password:
        
          password=password.replace("'", "''")
          
    query = cur.mogrify("select * from users WHERE name = '%s' AND password = crypt('%s', password);" % (username, password))
    #print query
    cur.execute(query)
      
    if cur.fetchone():
            query = cur.mogrify("select room1.name AS room1, room2.name AS room2, room3.name AS room3 FROM users LEFT OUTER JOIN room1 ON users.name = room1.name LEFT OUTER JOIN room2 ON users.name = room2.name LEFT OUTER JOIN room3 ON users.name = room3.name WHERE users.name = '%s';") % (username)
            #print(query)
            cur.execute(query)
            roomlist = cur.fetchall()
            room1 = roomlist[0][0]
            room2 = roomlist[0][1]
            room3 = roomlist[0][2]
            #print(roomlist[0][0])
            #print(roomlist[0][1])
            #print(roomlist[0][2])
            session['uuid'] = uuid.uuid1()
            session['username'] = username
            session['room1'] = '1'
            session['activeroom'] = 'room1'
            room1 = '1'
            if(room2 == username):
                room2 = '1'
                session['room2'] = '1'
            else:
                session['room2'] = '0'
            if(room3 == username):
                session['room3'] = '1'
                room3 = '1'
            else:
                session['room3'] = '0'
        
            activeroom = 'room1' 
            join_room('room1')
            users[session['uuid']] = {'username': username, 'room1': room1,'room2': room2, 'room3': room3}
            #print (users[session['uuid']])
            #print ('logged in')
            room=session['activeroom']
            print (room)
            emit('logged', username, room=room)
    else:
            username = ''
            password = ''

@socketio.on('account', namespace='/iss')        
def account(un, pw, r2, r3):
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    username = un
    password = pw
    #print(username)
    #print(password)
    print(r2)
    print(r3)

    if "'" in username:
        
          username=username.replace("'", "''")
        
    if "'" in password:
        
          password=password.replace("'", "''")
    
    query = cur.mogrify("insert into users (name, password) values ('%s', crypt('%s', gen_salt('bf')));" % (username, password))
    #print query
    cur.execute(query)
    conn.commit()
    
    if(r2):
        query = cur.mogrify("insert into room2 (name) values ('%s');" % (username))
        cur.execute(query)
        conn.commit()
    if(r3):
        query = cur.mogrify("insert into room3 (name) values ('%s');" % (username))
        cur.execute(query)
        conn.commit()
        
    session['uuid'] = uuid.uuid1()
    session['username'] = username
    users[session['uuid']] = {'username': username}
    #print (users[session['uuid']])
    #print ('logged in')
    room = session['activeroom']
    emit('logged', username, room=room)
    
    
@socketio.on('message', namespace='/iss')        
def message(text):
    global messages
    text=text
    name=users[session['uuid']]
    user = name['username']
    
    #print (name)
    #print (user)
    room = session['activeroom']
    if "'" in text:
        
          text=text.replace("'", "''")
          
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = cur.mogrify("INSERT INTO chatlog (name, text, room) VALUES ('%s','%s', '%s');" % (user, text, room))
    cur.execute(query)
    conn.commit()
    newmessage = {'text': text, 'name': user, "room": room}
    messages.append(newmessage.copy())
    
    print('name of room')
    print(room)
    print (newmessage)
    
    emit('message', newmessage.copy(), room=room)
    
@socketio.on('searching', namespace='/iss')        
def searching(searchQuery):
    returnmessages = {}
    reversemessages = []
    search=searchQuery
    room=session['activeroom']
    if "'" in search:
        
          search=search.replace("'", "''")
          
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = cur.mogrify("select name, text, room from chatlog WHERE name LIKE '%%%s%%' OR text LIKE '%%%s%%' AND room = '%s';" % (search, search,room))
    #print query
    cur.execute(query)
    searchedmessages = cur.fetchall()
    #print(searchedmessages)
    
    for m in searchedmessages:
        reroom = m[2]
        retex = m[1]
        renam = m[0]
        returnmessages={'text': retex, 'name': renam, 'room': reroom}
        #print(returnmessages)
        emit('searched', returnmessages)
        
@socketio.on('changeRoom', namespace='/iss')        
def changeRoom(newRoom):
    print('name of room')
    print(newRoom)
    oldroom=session['activeroom']
    print (oldroom)
    roomcheck = session[newRoom]
    print(roomcheck)
    if(roomcheck == '1'):
        session['activeroom'] = newRoom
        leave_room(oldroom)
        join_room(newRoom)
        
        conn = connectToDB()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = cur.mogrify("select name, text, room from chatlog WHERE room = '%s' ORDER BY id DESC LIMIT 10;" % (newRoom))
        cur.execute(query)
        pastmessages = cur.fetchall()
        pastmessagesdict = {}
        pastmessages.reverse()
        for message in pastmessages:
            pastmessagesdict={'text': message[1], 'name' : message[0], 'room' : message[2]}
            #print(pastmessagesdict)
            emit('message', pastmessagesdict)
            
    else:
        print('cannot join room')
        
    


#def updateRoster():
 #   names = []
#    for user_id in  users:
 #       if len(users[user_id]['username'])==0:
 #          names.append('Anonymous')
 #       else:
 #           names.append(users[user_id]['username'])
  #  socketio.emit('roster', names)    
    
@app.route('/')
def mainIndex():
            
    return app.send_static_file('index.html')
    


# start the server
if __name__ == '__main__':
        socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port =int(os.getenv('PORT', 8080)), debug=True)
