import googleapiclient.discovery
import googleapiclient.errors
import requests
import time
import random
from pymongo import MongoClient
from datetime import datetime
import json

url = 'http://central_broker_1:5001/publish'
player_list = ["SEN Tenz","TSM FTX WARDELL","100T Asuna"]
player_list_channel = ['UCckPYr9b_iVucz8ID1Q67sw', 'UCYg5NWc3B8RuarSFQR8n2VA', 'UCriJy6tyPtI5wrfZqXgRDag']
flag =0
random_number = 0



try:
        
        # conn = MongoClient(host='test_mongodb',
        #                     port=27017,
        #                     username='user',
        #                     password="password",
        #                     authSource="admin")
        # conn = MongoClient("mongodb://localhost:27017")
        conn = MongoClient("mongodb://user:password@mongodb2:27017")
    
        
        
except:  
        print("Could not connect to MongoDB")


def get_conn():
    list_of_db = conn.list_database_names()
    if "publisher_1_data" not in list_of_db:
        db = conn["publisher_1_data"]
        mydb = db["data"]
        

    else:
        db = conn.publisher_1_data
        mydb = db.data
        if mydb.find().count()!=0:
            mydb.remove({})
        

    



def scrape_players():
    global random_number
    global player_list
    api_key = 'AIzaSyCKkollyvp90wh9HRrEdiGI5ohs2G15EgU'
    youtube = googleapiclient.discovery.build('youtube', 'v3',developerKey=api_key)
    video_link = []
    video_id_ = []
    channel_id = []
    channel_title = []
    index_ = 0
    for player in player_list:
        request = youtube.search().list(
                part="snippet",
                q = player,
                type ="channel"
            )
        response = request.execute()
        channel_id.append(response['items'][0]['snippet']['channelId'])
        channel_title.append(response['items'][0]['snippet']['channelTitle'])
        # channel_id.append(player_list_channel[index_])
        # channel_title.append(player)
        # index_ = index_ + 1


    video_link = []
    video_id_ = []
    channel_id_final = []
    for i in range(len(channel_id)):
        print("lates video for channel : ",channel_title[i])
        request = youtube.activities().list(
                part="snippet,contentDetails",
                channelId=channel_id[i],
                maxResults=1
            )
        response = request.execute()
        if response['items'][0]['snippet']['type']=='upload':
            video_id = response['items'][0]['contentDetails']['upload']['videoId']
            video_id_.append(video_id)
            url = 'https://www.youtube.com/watch?v='
            url = url + video_id
            video_link.append(url)
            channel_id_final.append(channel_id[i])
            print(url)
            url = ""
        # video_id_.append('{}'.format(random_number))
        # video_link.append('this is the video link : {}'.format(random_number))
        # random_number = random_number + 1

    return channel_id,channel_title,video_link,video_id_

def check_new_data(channel_id_final,channel_title,video_link,video_id_):
    list_of_db = conn.list_database_names()
    index = 0
    index_2 = 0
    

    
    db = conn.publisher_1_data
    mydb = db.data
    if mydb.find().count()==0:                                         #TO check whether data exist in database or not
            updates = list()
            for video_id_value in video_id_:
                
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                data = {
                        'player_name':player_list[index_2],
                        'id' : video_id_value,
                        'topic_id' : channel_id_final[index_2],
                        'link' : video_link[index_2],
                        'date_time':dt_string
                        }
                data_update = {
                        'player_name':player_list[index_2],
                        'id' : video_id_value,
                        'topic_id' : channel_id_final[index_2],
                        'link' : video_link[index_2],
                        'date_time':dt_string
                }
                updates.append(data_update)
                mydb.insert_one(data)
                index_2 = index_2 + 1
            return updates
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
                            'player_name':player_list[index_2],
                            'id' : video_id_value,
                            'topic_id' : channel_id_final[index_2],
                            'link' : video_link[index_2],
                            'date_time':dt_string
                            }
                    data_update = {
                        'player_name':player_list[index_2],
                        'id' : video_id_value,
                        'topic_id' : channel_id_final[index_2],
                        'link' : video_link[index_2],
                        'date_time':dt_string
                    }
                    updates.append(data_update)
                    mydb.insert_one(data)
                index_2 = index_2 + 1
        
        # if len(updates) != 0:                                                   #Inform central broker of new data
        #     self.last_update_date_time = updates[len(updates)-1]['date_time']
        #     self.notify(updates,socketio,session_id)
            return updates
    
    


def scraper_main():
    flag =0
    while(flag == 0):
        try:
            message = {
                'message':'pub1'
            }
            message_to_send = json.dumps(message)
            r = requests.post(url,json=message_to_send)                    #First post request to check whether broker is up and running
            message = r.json()
            if message['message']=='Hello pub1':                               #Start collecting data after successful comms with broker
                print("client hi")
                channel_id_final,channel_title,video_link,video_id_ = scrape_players()
                updates = check_new_data(channel_id_final,channel_title,video_link,video_id_)
                print(updates)
                message = {
                    'message':updates
                }
                message_to_send = json.dumps(message)
                r = requests.post(url,json=message_to_send)
                broker_message = r.json()
                print("broker message",broker_message['message'])
            else:
                
                flag =1
            time.sleep(21600)
        except requests.exceptions.ConnectionError as err:
            print('server not reachable')
            time.sleep(5)

if __name__=="__main__":
    get_conn()
    scraper_main()
    