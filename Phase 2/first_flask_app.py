

from flask_socketio import SocketIO, emit
from flask import Flask, request,redirect,url_for,render_template,session
from pymongo import MongoClient
from time import sleep
from threading import Thread, Event
from scraping import *
from pub_sub import pub_sub_




player_list = ["SEN Tenz","TSM FTX WARDELL","100T Asuna","100T Hiko","SEN Sinatraa","SEN Sick","ShahZaM","ScreaM","AverageJonas","pkSidlol_"]
player_list_id = {}

thread = Thread()
thread_stop_event = Event()
session_id = dict()

app = Flask(__name__,template_folder='template')
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)
pub_sub_obj = pub_sub_()

try:
           
        conn = MongoClient("mongodb://user:password@mongodb2:27017")
        # conn = MongoClient("mongodb://localhost:27017")
        print(conn)
        
except:  
        print("Could not connect to MongoDB")





def scraping_func():
    print("Collecting data through Youtube API")
    
    while not thread_stop_event.isSet():
        topic_id,channel_title , links, video_id = scrape_players()
        if len(player_list_id) == 0:
            index = 0
            for player in player_list:
                player_list_id[player] = topic_id[index]
                index = index + 1

        pub_sub_obj.publisher(links,video_id,topic_id,player_list,socketio,session_id)
        socketio.sleep(21600)
        # socketio.sleep(300)

    
@socketio.on('my event', namespace='/test')
def test_connect():
    session_id[session['user']] = request.sid


@app.route("/")
def home():
    return render_template("login.html")

@app.route("/logout")
def logout():

    if session.get('user'):

        
        session_id.pop(session['user'])
        session['user'] = None
        
        return render_template("login.html")
    else:
        return render_template("login.html")
    

@app.route("/update_subs_func",methods=["POST","GET"])
def update_subs_func():

    if request.method == "POST":
        user_name = request.form['nm']
        pwd = request.form['no']
        
        topics = []
        data = {}
        
        if request.form['topic_1'] != "NA":
            topics.append(request.form['topic_1'])

        
        if request.form['topic_2'] != "NA":
            topics.append(request.form['topic_2'])

        
        if request.form['topic_3'] != "NA":
            topics.append(request.form['topic_3'])

        
        data['userName'] = user_name
        data['topics'] = topics
        pub_sub_obj.unsubscribe(data)
        data = pub_sub_obj.first_login_notify(user_name)
        if data==None:
            return render_template("outcome.html",info = "Please subscribe for updates")
        else:
            return render_template("home.html",data_ =data,user= user_name)

        

    

@app.route("/signUp",methods=["POST","GET"])
def signUp():
    if request.method == "POST":
        user_name = request.form['nm']
        pwd = request.form['no']
        
        

        topics = []
        data = {}
        
        if request.form['topic_1'] != "NA":
            topics.append(request.form['topic_1'])

        
        if request.form['topic_2'] != "NA":
            topics.append(request.form['topic_2'])

        
        if request.form['topic_3'] != "NA":
            topics.append(request.form['topic_3'])

        list_of_db = conn.list_database_names()
        

        if "login" not in list_of_db:
            db = conn["login"]
            mycol = db["credentials"]
            data = {
                "userName" : user_name,
                "password" : pwd}
            

            
            rec_id1 = mycol.insert_one(data)

            data['topics'] = topics
            
            pub_sub_obj.subscribe(data)
            
            return render_template("login.html")
        else:
            db = conn.login
            mydb = db.credentials
            user_credentials = mydb
            data = {
                "userName" : user_name,
                "password" : pwd}
            rec_id1 = mydb.insert_one(data)
            data['topics'] = topics
            pub_sub_obj.subscribe(data)

            return render_template("login.html")

@app.route("/click_on_signup")
def click_on_signup():
    
    return render_template("signUp.html")
    

@app.route("/update_subs")
def update_subs():

    if session.get('user'):
        return render_template("update_subs.html")
    else:
        return render_template("login.html")
    

    
@app.route("/data",methods=["POST","GET"])
def login():
    if request.method == "POST":
        user_name = request.form['nm']
        pwd = request.form['no']
        list_of_db = conn.list_database_names()
        
        if "login" not in list_of_db:
            
            db = conn["login"]
            mycol = db["credentials"]            
            data_temp = mycol.find()

            for values in data_temp:
                if values['userName'] == user_name:
                    if values['password'] == pwd:
                        

                        session["user"] = user_name
                        data = pub_sub_obj.first_login_notify(user_name)

                        if data==None:
                            return render_template("outcome.html",info = "Please subscribe for updates")
                        else:
                            return render_template("home.html",data_ =data,user= user_name)

                        
                        

                        
                    else:
                        return render_template("outcome.html",info="Invalid Password!")
                         
            

            return render_template("outcome.html",info="Invalid User Name ")
            
        else:
            db = conn.login
            mydb = db.credentials
            
            data = {
                "userName" : user_name,
                "password" : pwd
            }
            
            data2 = mydb.find()
            for values in data2:
                if values['userName'] == user_name:
                    if values['password'] == pwd:
                        # return render_template("home.html")
                        session["user"] = user_name
                        data = pub_sub_obj.first_login_notify(user_name)
                        if data==None:
                            return render_template("outcome.html",data_ = "Please subscribe for updates")
                        else:
                            return render_template("home.html",data_ =data,user= user_name)
                        
                    else:
                        # return render_template("outcome.html",info="Invalid Password")
                        return render_template("outcome.html",info="Invalid Password")
            

            # return render_template("outcome.html",info="Invalid User Name")
            return render_template("outcome.html",info="Invalid User Name")
   




if __name__ == "__main__":
    
    thread_obj = Thread(target=scraping_func)
    thread_obj.start()
    socketio.run(app,host = '0.0.0.0', debug=True,use_reloader=False )
    
    
    # app.run(host = '0.0.0.0' , debug=True,use_reloader=False)