from pymongo import MongoClient
from datetime import datetime
import json
# from flask_socketio import SocketIO, emit,send

class pub_sub_:
    def __init__(self):
        self.sub_list = None
        self.last_update_date_time = ""
        
           
        self.conn = MongoClient("mongodb://user:password@mongodb2:27017")
        # self.conn = MongoClient("mongodb://localhost:27017")

    def subscribe(self,data):
        
        data_insert = {
            
            'userName' : data['userName'] ,
            'topics' : data['topics']
        }

        

        list_of_db = self.conn.list_database_names()
        if "subscriptions" not in list_of_db:
            db = self.conn["subscriptions"]
            mycol = db["data"]
            mycol.insert_one(data_insert)
        else:
            db = self.conn.subscriptions
            mydb = db.data
            mydb.insert_one(data_insert)

    def unsubscribe(self,data):
        db = self.conn.subscriptions
        mydb = db.data

        
        

        myquery = { 'userName' : data['userName'] }
        newvalues = { "$set": { "topics": data['topics'] } }

        mydb.update_one(myquery, newvalues)

        
            

    def notify(self,updates,socketio,session_id):
        db = self.conn.subscriptions
        mydb = db.data

        results = mydb.find()
        

        for subs in results:
            topics = subs['topics']
            temp_list = []
            for results in updates:
                if results['player_name'] in topics:
                    temp_dict = dict()
                    
                    user = subs['userName']
                    session_id_value = session_id[user]
                    temp_dict = {
                        'player_name' : results['player_name'],
                        'link' : results['link']
                    }
                    temp_list.append(temp_dict)
            if(len(temp_list)!=0):
                obj = json.dumps(temp_dict)
                socketio.emit('newData', {'data':obj},room = session_id_value,namespace='/test')


        
    

    def publisher(self,links,video_id,topic_id,player_list,socketio,session_id):
        list_of_db = self.conn.list_database_names()
        index = 0
        index_2 = 0
        updates = []

        if "publisher_data" not in list_of_db:
            db = self.conn["publisher_data"]
            mydb = db["data"]

        else:
            db = self.conn.publisher_data
            mydb = db.data




        if mydb.find().count()==0:
         
            for video_id_value in video_id:
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                data = {
                        'player_name':player_list[index_2],
                        'id' : video_id_value,
                        'topic_id' : topic_id[index_2],
                        'link' : links[index_2],
                        'date_time':dt_string
                        }
                updates.append(data)
                mydb.insert_one(data)
                index_2 = index_2 + 1
            if len(updates) != 0:
                self.last_update_date_time = updates[len(updates)-1]['date_time']
                self.notify(updates,socketio,session_id)
                
        else:
            
            # data_values = mydb.find()
            # data_values_count = mydb.find().count()
            index = 0
            index_2 = 0
            updates = []
            
            for video_id_value in video_id:
                print(video_id_value)
                myquery = { 'id' : video_id_value }
                data_values = mydb.find(myquery).count()
                print(data_values)
                if data_values == 0:
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    data = {
                            'player_name':player_list[index_2],
                            'id' : video_id_value,
                            'topic_id' : topic_id[index_2],
                            'link' : links[index_2],
                            'date_time':dt_string
                            }
                    updates.append(data)
                    mydb.insert_one(data)
                index_2 = index_2 + 1
            if len(updates) != 0:
                self.last_update_date_time = updates[len(updates)-1]['date_time']
                self.notify(updates,socketio,session_id)
            
            

        
    def notify_particular_user(self,user_name):
        db = self.conn.subscriptions
        mydb = db.data
        myquery = { "userName": user_name }
       
        mydoc = mydb.find(myquery)
        
        db = self.conn.publisher_data
        mydb = db.data
        

        data = []

        for topics in mydoc[0]['topics']:

            output_result=dict()
            myquery = { 'player_name': topics }
            mydoc = mydb.find(myquery)
            
            
            output_result['player_name'] = mydoc[0]['player_name']
            output_result['link'] = mydoc[0]['link']


            data.append(output_result)

        if len(data)==0:
            return None
        
        return data

        




    def first_login_notify(self,user_name):
        if self.last_update_date_time==None:
            print("yes")
            return None
        else:
            return self.notify_particular_user(user_name)
