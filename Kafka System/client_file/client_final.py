from flask_socketio import SocketIO, emit, rooms
from flask import Flask, request,redirect,url_for,render_template,jsonify,session
import requests
import json
from time import sleep
from pymongo import MongoClient
# from pymongo import MongoClient


url = 'http://read_old_data:5001/new_sub'
url_3 = 'http://read_old_data:5001/unsubscribe_user'
url_4 = 'http://read_old_data:5001/subscribe'
app = Flask(__name__,template_folder='template')
app.jinja_env.add_extension('jinja2.ext.do')
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True


player_list = ['UCckPYr9b_iVucz8ID1Q67sw', 'UCYg5NWc3B8RuarSFQR8n2VA', 'UCriJy6tyPtI5wrfZqXgRDag']
player_list_={
    'SEN Tenz':'UCckPYr9b_iVucz8ID1Q67sw',
    "TSM FTX WARDELL" : 'UCYg5NWc3B8RuarSFQR8n2VA',
    "100T Asuna" :  'UCriJy6tyPtI5wrfZqXgRDag',
    "100T Hiko" : 'UCRN1XC7PnnTL5R_GbYOMCZg',
    "SEN Sinatraa" : 'UCABUGfcFJhffRFZxSl-mIiw',
    "SEN Sick": 'UCc8Er6GHj0casXQC9kOz-Ug',
    "ShahZaM": 'UCKNq_4ub5GACIkQfuVWEBtg',
    "ScreaM":'UCOpuMFmU3RyTeXejHWldXkA', 
    "AverageJonas":'UCg7fw-hJTvJBie_2T6l1dGg'
    
}
   
session_client_1 = dict()

socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)
try:
           
        # conn = MongoClient(host='test_mongodb',
        #                     port=27017,
        #                     username='user',
        #                     password="password",
        #                     authSource="admin")
        
        # conn = MongoClient("mongodb://localhost:27017")
        conn = MongoClient("mongodb://user:password@mongodb2:27017")
        print(conn)
        
except:  
        print("Could not connect to MongoDB")




#-------------------------------------Function to render login page------------------------------------------------------------
@app.route("/")
def home():
    return render_template("login.html")

#-------------------------------------Function to check login credentials------------------------------------------------------------
@app.route("/data",methods=["POST","GET"])
def login():
    print("*****************client 1 login*****************************************")
    if request.method == "POST":
        user_name = request.form['nm']
        pwd = request.form['no']
        list_of_db = conn.list_database_names()
        
        if "login_client_1" not in list_of_db:
            
            db = conn["login_client_1"]
            mycol = db["credentials"]            
            data_temp = mycol.find()

            for values in data_temp:
                if values['userName'] == user_name:
                    if values['password'] == pwd:
                        
                        session['user']=user_name
                        # session["user"] = user_name
                        # data = pub_sub_obj.first_login_notify(user_name)
                        
                        
                        data = requests.get(url,json={'userName':user_name})
                        message_from_broker = data.json()

                        print("*****************Data from broker*****************************************",message_from_broker)

                        temp_list = []
                        if len(message_from_broker['updates'])==0:
                            return render_template("outcome.html",info = "Please subscribe for updates")
                        else:
                            return render_template("home.html",data_=message_from_broker['updates'],user= user_name,dup = temp_list)     #this will send the updates for the exsisting user who has logged in again
                    else:
                        return render_template("outcome.html",info="Invalid Password!")
                         
            

            return render_template("outcome.html",info="Invalid User Name ")
            
        else:
            db = conn.login_client_1
            mydb = db.credentials
            
            data = {
                "userName" : user_name,
                "password" : pwd
            }
            
            data2 = mydb.find()
            for values in data2:
                if values['userName'] == user_name:
                    if values['password'] == pwd:
                        
                        session['user']=user_name
                        data = requests.get(url,json={'userName':user_name})
                        message_from_broker = data.json()
                        temp_list = []
                        # message_from_broker = json.loads(parse_message)
                        
                        if len(message_from_broker['updates'])==0:
                            return render_template("outcome.html",info = "Please subscribe for updates")
                        else:
                            return render_template("home.html",data_=message_from_broker['updates'],user= user_name,dup = temp_list)
                        
                    else:
                        # return render_template("outcome.html",info="Invalid Password")
                        return render_template("outcome.html",info="Invalid Password")
            

            # return render_template("outcome.html",info="Invalid User Name")
            return render_template("outcome.html",info="Invalid User Name")


#-------------------------------------Function to send notifications------------------------------------------------------------
@app.route("/notify_user",methods=["POST","GET"])
def notify_user():
    #if there are no user logged in, will have to inform backend to stop pushing messages
    print('+++++++++++++++++++++++++ INSIDE NOTIFY USer+++++++++++++++++++++++++')
    message_from_broker = request.json
    updates_user = message_from_broker['updates']
    user_name = message_from_broker['userName']
    print('+++++++++++++++++++++++++ INSIDE NOTIFY USer+++++++++++++++++++++++++',message_from_broker)
    if request.method == "POST":
        if user_name in session_client_1.keys(): 
            message = {
                'message' : 'Data sent'
            }
            obj = json.dumps(message_from_broker)
            socketio.emit('updated_list', {'data':obj},namespace='/test',room=session_client_1[user_name])
            return jsonify(message)

        elif user_name == 'consumer_1' or user_name == 'consumer_2' or user_name=='consumer_3':
            message_to_send = {
                'message' : 'Hello consumer_1'
            }
            return jsonify(message_to_send)

        else:
            message = {
                'message' : 'User is not present'
            }
            return jsonify(message)

#-------------------------------------Function to register user------------------------------------------------------------

@app.route("/signUp",methods=["POST","GET"])
def signUp():
    if request.method == "POST":
        user_name = request.form['nm']
        pwd = request.form['no']

        topics = []
        data = {}
        
        if request.form['topic_1'] != "NA":
            topics.append(player_list_[request.form['topic_1']])

        
        if request.form['topic_2'] != "NA":
            topics.append(player_list_[request.form['topic_2']])

        
        if request.form['topic_3'] != "NA":
            topics.append(player_list_[request.form['topic_3']])

        list_of_db = conn.list_database_names()
        

        if "login_client_1" not in list_of_db:
            db = conn["login_client_1"]
            mycol = db["credentials"]
            data = {
                "userName" : user_name,
                "password" : pwd}
            

            
            rec_id1 = mycol.insert_one(data)

            user_sub_details = {
                'userName':user_name,
                'topics':topics
            }
            
            if "subscriptions_1_data" not in list_of_db:
                db = conn["subscriptions_1_data"]
                mycol = db["data"]
                mycol.insert_one(user_sub_details)
            else:
                db = conn.subscriptions_1_data
                mydb = db.data
                mydb.insert_one(user_sub_details)
            # pub_sub_obj.subscribe(data)
            
            return render_template("login.html")
        else:
            db = conn.login_client_1
            mydb = db.credentials
            user_credentials = mydb
            data = {
                "userName" : user_name,
                "password" : pwd}
            rec_id1 = mydb.insert_one(data)
            data['topics'] = topics
            user_sub_details = {
                'userName':user_name,
                'topics':topics
            }
            db = conn.subscriptions_1_data
            mydb = db.data
            mydb.insert_one(user_sub_details)
            return render_template("login.html")

@app.route("/update_subs_func",methods=["POST","GET"])
def update_subs_func():

    if request.method == "POST":
        user_name = request.form['nm']
        pwd = request.form['no']
        
        topics = []
        data = {}
        
        if request.form['topic_1'] != "NA":
            topics.append(player_list_[request.form['topic_1']])

        
        if request.form['topic_2'] != "NA":
            topics.append(player_list_[request.form['topic_2']])

        
        if request.form['topic_3'] != "NA":
            topics.append(player_list_[request.form['topic_3']])

        
        data['userName'] = user_name
        data['topics'] = topics
        # pub_sub_obj.unsubscribe(data)
        # data = pub_sub_obj.first_login_notify(user_name)
        message_to_send = {
            'userName':user_name,
            'topics':topics
        }
        data_unsub = requests.post(url_3,json=message_to_send)
        message_from_broker = data_unsub.json()
        print('^^^^^^^^^^^^^^^^^^ Data after unsub ^^^^^^^^^^^^',message_from_broker)
        data = requests.get(url,json={'userName':user_name , 'topics':topics})
        message_from_broker = data.json()
        temp_list = []
        print('--------------------------------------data with updated subscriptions for user---------------------')
        if data==None:
            return render_template("outcome.html",info = "Please subscribe for updates")
        else:
            return render_template("home.html",data_ =message_from_broker['updates'],user= message_from_broker['userName'],dup=temp_list)


@app.route("/subscribe",methods=["POST","GET"])
def subscribe():

    if request.method == "POST":
        user_name = request.form['nm']
        pwd = request.form['no']
        
        topics = []
        data = {}
        
        if request.form['topic_1'] != "NA":
            topics.append(player_list_[request.form['topic_1']])

        
        if request.form['topic_2'] != "NA":
            topics.append(player_list_[request.form['topic_2']])

        
        if request.form['topic_3'] != "NA":
            topics.append(player_list_[request.form['topic_3']])

        
        data['userName'] = user_name
        data['topics'] = topics
        # pub_sub_obj.unsubscribe(data)
        # data = pub_sub_obj.first_login_notify(user_name)
        message_to_send = {
            'userName':user_name,
            'topics':topics
        }
        data_unsub = requests.post(url_4,json=message_to_send)
        message_from_broker = data_unsub.json()
        print('^^^^^^^^^^^^^^^^^^ Data after unsub ^^^^^^^^^^^^',message_from_broker)
        data = requests.get(url,json={'userName':user_name , 'topics':topics})
        message_from_broker = data.json()
        temp_list = []
        print('--------------------------------------data with updated subscriptions for user---------------------')
        if data==None:
            return render_template("outcome.html",info = "Please subscribe for updates")
        else:
            return render_template("home.html",data_ =message_from_broker['updates'],user= message_from_broker['userName'],dup=temp_list)

@app.route("/update_subs")
def update_subs():
    return render_template("update_subs.html")

@app.route("/logout")
def logout():
    user_name = session['user']
    print('+++++++++++++++++session before logout+++++++',session['user'],session_client_1)
    del session_client_1[user_name]
    session.clear()
    print('+++++++++++++++++session before logout+++++++',session,session_client_1)
    return render_template("login.html")


@app.route("/click_on_signup")
def click_on_signup():
    
    return render_template("signUp.html")

@app.route("/click_on_sub")
def click_on_sub():
    
    return render_template("subscribe.html")

@socketio.on('my event', namespace='/test')
def test_connect():
    session_client_1[session['user']] = request.sid
    print('+++++++++++++++++++++++++++++Session details:',session_client_1[session['user']])



if __name__ == '__main__':
    app.run(host = '0.0.0.0',port=5000)
    # socketio.run(app,host = '0.0.0.0',port=5000, debug=True,use_reloader=False )



