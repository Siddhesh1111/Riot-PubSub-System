import json
import json
import requests
import time
from flask_socketio import SocketIO, emit
from flask import Flask, request,redirect,url_for,render_template,session,jsonify
from threading import Thread, Event
from pymongo import MongoClient


app = Flask(__name__)
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


@app.route('/new_sub',methods=["POST","GET"])  
def new_sub():
    print("****************Central Broker 1 new sub**********************************")
    if request.method=="GET":                                                     #new sub from sub container with user name and topic_list
        client_message = request.json
        
        client_user_name = client_message['userName']
        

        db = conn.subscriptions_1_data
        mydb = db.data
        
        myquery = {
            'userName':client_user_name
        }
        data_values = mydb.find(myquery)

        
        topics = list()
        for user_details in data_values:
            topics = user_details['topics']
  
        message_to_send_broker = {
            'userName':client_user_name,
            'topics' : topics
        }
        print("****************Central Broker 1 message for rand**********************************",message_to_send_broker)
        
        
        db = conn.publisher_1_data
        mydb = db.data
        data_to_display = []
        video_details = mydb.find()

        for topic in topics:
            print(topic)
            for video in video_details:
                print("channel_id------------------------------------------",video['topic_id'])
                print("++++++++++++++++++++channel_id------------------------------------------",topic)
                if topic == video['topic_id']:
                    data = {
                        'player_name':video['player_name'],
                        'id' : video['id'],
                        'topic_id' : video['topic_id'],
                        'link' : video['link'],
                        'print':0
                        }
                    data_to_display.append(data)
                    
            video_details = mydb.find()



        db = conn.publisher_2_data
        mydb = db.data

        video_details = mydb.find()

        for topic in topics:
            print(topic)
            for video in video_details:
                print("channel_id------------------------------------------",video['topic_id'])
                print("++++++++++++++++++++channel_id------------------------------------------",topic)
                if topic == video['topic_id']:
                    data = {
                        'player_name':video['player_name'],
                        'id' : video['id'],
                        'topic_id' : video['topic_id'],
                        'link' : video['link'],
                        'print':0
                        }
                    data_to_display.append(data)
                    
            video_details = mydb.find()


        db = conn.publisher_3_data
        mydb = db.data

        video_details = mydb.find()

        for topic in topics:
            print(topic)
            for video in video_details:
                print("channel_id------------------------------------------",video['topic_id'])
                print("++++++++++++++++++++channel_id------------------------------------------",topic)
                if topic == video['topic_id']:
                    data = {
                        'player_name':video['player_name'],
                        'id' : video['id'],
                        'topic_id' : video['topic_id'],
                        'link' : video['link'],
                        'print':0
                        }
                    data_to_display.append(data)
                    
            video_details = mydb.find()


        message_to_send={
            'userName' : user_details['userName'],
            'updates':data_to_display
        }
        
       
        return jsonify(message_to_send)

@app.route('/unsubscribe_user',methods=["POST","GET"])
def unsubscribe_user():
    if request.method=="POST":  
        db = conn.subscriptions_1_data
        mydb = db.data
        user_details = request.json
        myquery = { 'userName' : user_details['userName'] }
        # newvalues = { "$set": { "topics": user_details['topics'] } }
        # mydb.update_one(myquery, newvalues)
        sub_details = mydb.find(myquery)
        topic = list()
        for user in sub_details:
            topic = user['topics']
        

        for value in user_details['topics']:
            if value in topic:
                topic.remove(value)
        
        print('^^^^^^^^^^^^^^^^^^^^ New Values after update ^^^^^^^^^^^^^^^^^^',topic)
        newvalues = { "$set": { "topics": topic } }
        mydb.update_one(myquery, newvalues)

        message_to_send={
            'message' : 'Subscriptions Updated',
            'topic' : topic
        }
        return jsonify(message_to_send)


@app.route('/subscribe',methods=["POST","GET"])
def subscribe():
    if request.method=="POST":  
        db = conn.subscriptions_1_data
        mydb = db.data
        user_details = request.json
        myquery = { 'userName' : user_details['userName'] }
        # newvalues = { "$set": { "topics": user_details['topics'] } }
        # mydb.update_one(myquery, newvalues)
        sub_details = mydb.find(myquery)
        topic = list()
        for user in sub_details:
            topic = user['topics']
        

        for value in user_details['topics']:
            if value in topic:
                continue
            else:
                topic.append(value)

        print('^^^^^^^^^^^^^^^^^^^^ New Values after sub ^^^^^^^^^^^^^^^^^^',topic)
        newvalues = { "$set": { "topics": topic } }
        mydb.update_one(myquery, newvalues)

        message_to_send={
            'message' : 'Subscriptions Updated',
            'topic' : topic
        }
        return jsonify(message_to_send)




if __name__ == '__main__':
    socketio.run(app,host = '0.0.0.0',port=5001, debug=True,use_reloader=False )
    