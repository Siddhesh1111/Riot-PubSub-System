from pymongo import MongoClient
from datetime import datetime
import json
import requests
from sys import stdout
import time

class pub_sub_:
    def __init__(self):
        self.sub_list = None
        self.current_cb = 'cb1'                                                     #sub list with user_name and topic_id from YT
        self.conn = MongoClient("mongodb://user:password@mongodb2:27017")
        # self.conn = MongoClient("mongodb://localhost:27017")
        # self.conn = MongoClient(host='test_mongodb',
        #                     port=27017,
        #                     username='user',
        #                     password="password")
        self.url = "http://client_1:5000/notify_user"
        self.url_update_subs_broker2 = "http://central_broker_2:5003/update_subs_other_broker"
        self.url_update_subs_broker3 = "http://central_broker_3:5005/update_subs_other_broker"
        self.url_broker_data_2 = "http://central_broker_2:5003/get_broker_data"
        self.url_broker_data_3 = "http://central_broker_3:5005/get_broker_data"
        self.url_update_for_broker_2 = "http://central_broker_2:5003/update_from_broker"
        self.url_update_for_broker_3 = "http://central_broker_3:5005/update_from_broker"
        self.cb_topic_map = {
            'cb1' : ['UCckPYr9b_iVucz8ID1Q67sw','UCYg5NWc3B8RuarSFQR8n2VA','UCriJy6tyPtI5wrfZqXgRDag'],
            'cb2': ['UCRN1XC7PnnTL5R_GbYOMCZg','UCABUGfcFJhffRFZxSl-mIiw','UCc8Er6GHj0casXQC9kOz-Ug'],
            'cb3':['UCKNq_4ub5GACIkQfuVWEBtg', 'UCOpuMFmU3RyTeXejHWldXkA', 'UCg7fw-hJTvJBie_2T6l1dGg']
            
        }
        self.db = self.conn.subscriptions_1_data
        self.mydb = self.db.data
        if self.mydb.find().count()!=0:
            self.mydb.remove({})
        
        

        

    #----------------------------------------------Function to get topic and cb------------------------------------------------
    def get_topic_cb(self,topic):
        print("********************Central Broker 1 get topic cb***********************")
        for key in self.cb_topic_map.keys():
            if topic in self.cb_topic_map[key]:
                return key
            else:
                continue


    #----------------------------------------------Function to implement rand algo------------------------------------------------
    def rand_func(self,user_details):
        cb1_topics = list()
        cb2_topics = list()
        cb3_topics = list()
        final_updates = []
        for topic in user_details['topics']:
            broker = self.get_topic_cb(topic)
            if broker == self.current_cb:
                cb1_topics.append(topic)
            elif broker == 'cb2':
                cb2_topics.append(topic)
            else:
                cb3_topics.append(topic)
        
        if len(cb2_topics)!=0:
            message_to_send = {
                'userName' : 'cb1',
                'topics' : cb2_topics
            }
            print("********************Central Broker 1 sending message to cb2***********************",message_to_send)
            r = requests.get(self.url_broker_data_2,json=message_to_send)
            updates_from_broker = r.json()
            print('***************************Message from cb2***************** : ',updates_from_broker)
            for update in updates_from_broker['updates']:
                final_updates.append(update)
        
        if  len(cb1_topics)!=0:
            message_to_send = {
                'userName' : user_details['userName'],
                'topics' : cb1_topics
            }
            updates_from_current_cb = self.notify_new_user(message_to_send)
            print('********************Message from cb1************************8 : ',updates_from_current_cb)
            for update in updates_from_current_cb['updates']:
                final_updates.append(update)

        if len(cb3_topics)!=0:
            message_to_send = {
                'userName' : 'cb1',
                'topics' : cb3_topics
            }
            r = requests.get(self.url_broker_data_3,json=message_to_send)
            updates_from_broker = r.json()
            print('--------------------------Message from cb3 : ',updates_from_broker)
            for update in updates_from_broker['updates']:
                final_updates.append(update)

        message_to_show={
            'userName' : user_details['userName'],
            'updates':final_updates
        }
        print('**********************************Message user will see********************',message_to_show)      
        return message_to_show

    #-----------------------------------------function to handle update subscriptions-----------------------------------------
    def unsubscribe(self,user_details):
        db = self.conn.subscriptions_1_data
        mydb = db.data


        if user_details['userName']=='cb2' or user_details['userName']=='cb3':
            myquery = { 'userName' : user_details['userName'] }
            records = mydb.find(myquery)
            updated_topics = list()
            if mydb.find(myquery).count()!=0:

                records = mydb.find(myquery)
                for record in records:
                    topics_ = record['topics']
                
                for top in topics_:
                    updated_topics.append(top)

                for top in user_details['topics']:
                    if top not in updated_topics:
                        updated_topics.append(top)
                myquery = { 'userName' : user_details['userName'] }
                newvalues = { "$set": { "topics": updated_topics } }
                mydb.update_one(myquery, newvalues)
            
            else:
                print("******************there was not data to unsub hence adding**************",user_details)
                self.subscribe(user_details)

        else:

            cb1_topics = list()
            cb2_topics = list()
            cb3_topics = list()
            final_updates = []
            for topic in user_details['topics']:
                broker = self.get_topic_cb(topic)
                if broker == self.current_cb:
                    cb1_topics.append(topic)
                elif broker == 'cb2':
                    cb2_topics.append(topic)
                else:
                    cb3_topics.append(topic)


            if len(cb2_topics)!=0:
                message_to_send = {
                    'userName' : 'cb1',
                    'topics' : cb2_topics,
                    
                }
                print("********************Central Broker 1 sending message to cb2 to unsub***********************",message_to_send)
                r = requests.post(self.url_update_subs_broker2,json=message_to_send)
                updates_from_broker = r.json()
                print('***************************Message from cb2 unsub***************** : ',updates_from_broker)
            
            
            
            myquery = { 'userName' : user_details['userName'] }
            newvalues = { "$set": { "topics": user_details['topics'] } }

            mydb.update_one(myquery, newvalues)
            print('********************Message from cb1 unsubscribe************************8 : ')
                

            if len(cb3_topics)!=0:
                message_to_send = {
                    'userName' : 'cb1',
                    'topics' : cb3_topics,
                    
                }
                print('--------------------------Message from cb3 to unsub : ',message_to_send)
                r = requests.post(self.url_update_subs_broker3,json=message_to_send)
                updates_from_broker = r.json()
                print('***************************Message from cb2 unsub***************** : ',updates_from_broker)
            
        

        

    #----------------------------------------------------Function to get user topics-------------------------------------------
    def get_userTopics(self,userName):
        db = self.conn.subscriptions_1_data
        mydb = db.data
        
        myquery = {
            'userName':userName
        }
        data_values = mydb.find(myquery)

        
        topic = list()
        for user_details in data_values:
            topic = user_details['topics']
            
        print('-----------------------------------------------------------------',file=stdout)
        print(topic,file=stdout)
        return topic

    #--------------------------------------------Functions to add subscriptions----------------------------------------
    def subscribe(self,user_details):
        
        print('*********************Inside cb1 subscribe*********************',user_details)
        
        user_sub_details = {
            'userName' : user_details['userName'],
            'topics' : user_details['topics']
        }

        if user_details['userName']=='cb2' or user_details['userName']=='cb3':
            db = self.conn.subscriptions_1_data
            mydb = db.data
            final_list = list()
            myquery = {
                'userName': user_details['userName']
            }
            if mydb.find(myquery).count()!=0:
                myquery = {
                'userName': user_details['userName']
                }
                records = mydb.find(myquery)
                topic_ = list()
                for record in records:
                    topic_ = record['topics']
                for top in topic_:
                    final_list.append(top) 
                for top in user_details['topics']:
                    if top not in topic_:
                        final_list.append(top)
                myquery = { 'userName' : user_details['userName'] }
                newvalues = { "$set": { "topics": final_list } }
                mydb.update_one(myquery, newvalues)
            else:
                db = self.conn.subscriptions_1_data
                mydb = db.data
                mydb.insert_one(user_sub_details)
        else:
            list_of_db = self.conn.list_database_names()
            if "subscriptions_1_data" not in list_of_db:
                db = self.conn["subscriptions_1_data"]
                mycol = db["data"]
                mycol.insert_one(user_sub_details)
            else:
                db = self.conn.subscriptions_1_data
                mydb = db.data
                mydb.insert_one(user_sub_details)
        
        
        return 'Subscription added'

    #--------------------------------------------------------------Function to publish new data-----------------------------------
    def publisher(self,update_list):
        list_of_db = self.conn.list_database_names()
        if "subscriptions_1_data" not in list_of_db:
            print("No subscribers")
            return

        db = self.conn.subscriptions_1_data
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
            self.notify(updates_for_sub,subs['userName'])
            # myquery = { 'id' : video_id_value }
            # data_values = mydb.find(myquery).count()
            
        
    #--------------------------Function to notify when data is published-----------------------------------------------
    def notify(self,updates_for_sub,user_name):
        # try:
        #     message_to_send={
        #         'userName' : user_name,
        #         'updates':updates_for_sub
        #     }
        #     r = requests.post(self.url,json=message_to_send)
        #     received_message = r.json()
        #     print(received_message)
        # except requests.exceptions.ConnectionError as err:
        #     print('server not reachable')
        
        try:

            print('********************Inside notify 1 publisher***************')
            message_to_send={
                'userName' : user_name,
                'updates':updates_for_sub
            }
            if user_name == 'cb2' and  len(updates_for_sub)!=0:
                print('********************Message for broker 2******************************8',message_to_send)
                r = requests.post(self.url_update_for_broker_2,json=message_to_send)
                received_message = r.json()
                print('********************Message received from broker 2******************************8',received_message)
            if user_name == 'cb3' and len(updates_for_sub)!=0:
                print('********************Message for broker 3******************************8',message_to_send)
                r = requests.post(self.url_update_for_broker_3,json=message_to_send)
                received_message = r.json()
                print('********************Message received from broker 3******************************8',received_message)
            if (user_name != 'cb3' or user_name != 'cb2') and len(updates_for_sub)!=0:
                r = requests.post(self.url,json=message_to_send)
                received_message = r.json()
                print(received_message)
            
            
            return 
        except requests.exceptions.ConnectionError as err:
            print('server not reachable')
            
            
         
    #--------------------------Function to notify when user logs in first time-----------------------------------------------
    def notify_new_user(self,user_details):
        db = self.conn.publisher_1_data
        mydb = db.data
        data_to_display = []
        video_details = mydb.find()
        for topic in user_details['topics']:
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
        
        print("---------------------------------------------",message_to_send)
        
        return message_to_send
        
            
    
    