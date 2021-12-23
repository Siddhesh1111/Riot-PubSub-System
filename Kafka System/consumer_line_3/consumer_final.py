import re
from kafka import KafkaProducer
from kafka import KafkaConsumer
import json
import kafka
import json
import requests
import time
from flask_socketio import SocketIO, emit
from flask import Flask, request,redirect,url_for,render_template,session,jsonify
from threading import Thread, Event
from pymongo import MongoClient
from datetime import datetime

# from threading import Thread, Event

url = 'http://client:5000/notify_user'


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

def check_client():
    while(True):
        try:
            message = {
                'updates':'consumer_1',
                'userName':'consumer_1'
            }
            # message_to_send = json.dumps(message)
            r = requests.post(url,json=message)
            message = r.json()
            if message['message']=='Hello consumer_1':
                print('&&&&&&&&&&&&&&&&&&&&&&server Reachable&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
                return
        except requests.exceptions.ConnectionError as err:
            print('&&&&&&&&&&&&&&&&&&&&&&server not reachable&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
            time.sleep(1)

def create_update(update_list):

    list_of_db = conn.list_database_names()
    if "subscriptions_1_data" not in list_of_db:
        print("No subscribers")
        return

    db = conn.subscriptions_1_data
    mydb = db.data
    user_sub_details = mydb.find()
    for subs in user_sub_details:
        updates_for_sub = list()
        for updates in update_list:
            updated_topic_id = updates['topic_id']
            updated_video_id = updates['id']
            updated_video_link = updates['link']
            if updated_topic_id in subs['topics']:
                updates_for_sub.append(updates)
        message = {
            'userName' : subs['userName'],
            'updates':updates_for_sub
        }
        data = requests.post(url,json=message)
        message = data.json()
        print('********************************* REPLY from client************************',message['message'])


def check_new(new_data):
    list_of_db = conn.list_database_names()
    index = 0
    index_2 = 0
    video_id_ = list()
    video_id_.append(new_data['id'])

    
    db = conn.publisher_3_data
    mydb = db.data
    if mydb.find().count()==0:                                         #TO check whether data exist in database or not
            updates = list()
            for video_id_value in video_id_:
                
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                data = {
                        'player_name':new_data['player_name'],
                        'id' : video_id_value,
                        'topic_id' : new_data['topic_id'],
                        'link' : new_data['link'],
                        'date_time':new_data['date_time']
                        }
                data_update = {
                        'player_name':new_data['player_name'],
                        'id' : video_id_value,
                        'topic_id' : new_data['topic_id'],
                        'link' : new_data['link'],
                        'date_time':new_data['date_time']
                }
                updates.append(data_update)
                mydb.insert_one(data)
                index_2 = index_2 + 1
            if len(updates)!=0:
                return True
            else:
                return False
    else:                                                                                   #If database is created compare api data with database data
            index = 0
            index_2 = 0
            updates = list()
            
            for video_id_value in video_id_:
                data = dict()
                print(video_id_value)
                myquery = { 'id' : video_id_value }
                data_values = mydb.find(myquery).count()
                print(data_values)
                if data_values == 0:   
                                                                #if the api data is new data enter value in db
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    data = {
                            'player_name':new_data['player_name'],
                        'id' : video_id_value,
                        'topic_id' : new_data['topic_id'],
                        'link' : new_data['link'],
                        'date_time':new_data['date_time']
                            }
                    data_update = {
                        'player_name':new_data['player_name'],
                        'id' : video_id_value,
                        'topic_id' : new_data['topic_id'],
                        'link' : new_data['link'],
                        'date_time':new_data['date_time']
                    }
                    updates.append(data_update)
                    mydb.insert_one(data)
                index_2 = index_2 + 1
            if len(updates)!=0:
                return True
            else:
                return False


def kafka_listener(consumer_obj):
    print('+++++++++++++++++++++++++++++++++++++++++++++++++',consumer_obj)
    consumer_obj.subscribe(topics=['UCriJy6tyPtI5wrfZqXgRDag'])
        
    for msg in consumer_obj:
        json_obj = json.loads(msg.value)
        # player_name = json_obj['player_name']
        message = {
                'updates':[json_obj],
                'userName':'UCriJy6tyPtI5wrfZqXgRDag'
            }
        result = check_new(json_obj)
        if result:
            create_update([json_obj])
        else:
            print('@@@@@@@@@@@@@@@@@@@@@@ No New Data @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        # print('///////////////////CONSUMER1//////////////////REgistered User = {}'.format(message)


def get_consumer_obj():
    while(True):
        try:
            print('-------------------Connected to server1-------------------------------')
            consumer = KafkaConsumer(
                bootstrap_servers = 'kafka2:8081',
                auto_offset_reset = 'earliest',
                group_id='consumer-group-a'
            )
            
            print('-------------------Connected to server1-------------------------------')
            # consumer.seek_to_beginning()
            return consumer
        except kafka.errors.NoBrokersAvailable as e:
            print(e)
            print('---------------waiting for kaka-----------')
            time.sleep(1)


def get_conn():
    list_of_db = conn.list_database_names()
    if "publisher_3_data" not in list_of_db:
        db = conn["publisher_3_data"]
        mydb = db["data"]
        

    else:
        db = conn.publisher_3_data
        mydb = db.data
        if mydb.find().count()!=0:
            mydb.remove({})

if __name__ == '__main__':
    get_conn()
    consumer_obj = get_consumer_obj()
    check_client()
    kafka_listener(consumer_obj)
    
    
    

