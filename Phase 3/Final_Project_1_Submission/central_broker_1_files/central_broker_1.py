from flask_socketio import SocketIO, emit
from flask import Flask, request,redirect,url_for,render_template,session,jsonify
from pymongo import MongoClient
from time import sleep
from central_broker_pub_sub import pub_sub_
import json
from bson.json_util import dumps
from sys import stdout

player_list = ['UCckPYr9b_iVucz8ID1Q67sw', 'UCYg5NWc3B8RuarSFQR8n2VA', 'UCriJy6tyPtI5wrfZqXgRDag']
topic_id = []
pub_sub_obj = pub_sub_()
app = Flask(__name__,template_folder='template')
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)


#-----------------------------------------------------Function to handle unsub from other broker----------------------------
@app.route('/update_subs_other_broker',methods=["POST","GET"])
def update_subs_other_broker():
    if request.method=="POST":
        broker_message = request.json
        print("***********************************Message from other broker to unsub, broker************8",broker_message['userName'])
        pub_sub_obj.unsubscribe(broker_message)
        message_to_send = {
            'message' : 'received and notified'
        }
        return jsonify(message_to_send)

#-----------------------------------------------------Function to handle updates from other broker----------------------------
@app.route('/update_from_broker',methods=["POST","GET"])
def update_from_broker():
    
    if request.method=="POST":
        
        broker_message = request.json
        print("***********************************Message from broker************8",broker_message['userName'])
        pub_sub_obj.publisher(broker_message['updates'])
        message_to_send = {
            'message' : 'received and notified'
        }
        print("****************Central Broker 1 message for rand**********************************",broker_message)
        
        return jsonify(message_to_send)

    

#-----------------------------------------------------Function to handle data requested from other broker----------------------------
@app.route('/get_broker_data',methods=["POST","GET"]) 
def get_broker_data():
    if request.method=="GET":
        client_message = request.json
        print('------------------------------request for topics from broker : ',client_message['userName'],client_message['topics'])
        pub_sub_obj.subscribe(client_message)
        updates  = pub_sub_obj.notify_new_user(client_message)
        return jsonify(updates)


#-------------------------------------method to handle unsubscribe-----------------------------------------------------------------
@app.route('/unsubscribe_user',methods=["POST","GET"]) 
def unsubscribe_user():
    if request.method=="POST":
        print("*********************************Message to unsub user*************",)
        client_message = request.json
        user_name = client_message['userName']
        topics = client_message['topics']
        pub_sub_obj.unsubscribe(client_message)
        # message_to_send = pub_sub_obj.notify_new_user(client_message)
        message_to_send = pub_sub_obj.rand_func(client_message)
        return jsonify(message_to_send)


#--------------------------------------------------------method to handle commuication with publisher container----------------------
@app.route('/publish',methods=["POST","GET"])                 
def publish():
    if request.method=="POST":
        client_message = json.loads(request.json)
        print("----------------CENTRAL BROKER PUBLISH METHOD-----------------",client_message)
        if client_message['message'] == 'pub1':
            server_message =  {
                "message":"Hello pub1"
            }

            return jsonify(server_message)
        elif type(client_message['message']) == list:       #Client has send a list with update
            print("hi")

            if(len(client_message['message'])==0):
                print("No new data from publisher")
                server_message =  {
                    "message":"No new data from publisher"
                }
                return jsonify(server_message)
            else:
                print("Received new Data")
                pub_sub_obj.publisher(client_message['message'])
                server_message =  {
                    "message":"Data added successfuly"
                }
                
                return jsonify(server_message)
        else:
            server_message =  {
                "message":"Who are you?"
            }
            return jsonify(server_message)

#-------------------------------------Function to add subscriptions-----------------------------------------------------------
@app.route('/add_sub',methods=["POST","GET"])
def add_sub():
    print("****************Central Broker add sub**********************************")
    if request.method=="POST":
        client_message = request.json
        message = pub_sub_obj.subscribe(client_message)
        message_to_send = {
            'message' : message
        }
        return json.dumps(message_to_send)

#---------------------------------------Function to notify new user logged in------------------------------------------------
@app.route('/new_sub',methods=["POST","GET"])  
def new_sub():
    print("****************Central Broker 1 new sub**********************************")
    if request.method=="GET":                                                     #new sub from sub container with user name and topic_list
        client_message = request.json
        # client_message = json.loads(client_message_)
        client_user_name = client_message['userName']
        topics = pub_sub_obj.get_userTopics(client_user_name)
        
        message_to_send_broker = {
            'userName':client_user_name,
            'topics' : topics
        }
        print("****************Central Broker 1 message for rand**********************************",message_to_send_broker)
        message_to_send = pub_sub_obj.rand_func(message_to_send_broker)
        
        # message_to_send = pub_sub_obj.notify_new_user(message_to_send_broker)
        
       
        return jsonify(message_to_send)

if __name__ == '__main__':
    # app.run(host = '0.0.0.0',port=5001)
    socketio.run(app,host = '0.0.0.0',port=5001, debug=True,use_reloader=False )
