from logging import error
import time
import json
from kafka import KafkaProducer
from kafka import KafkaConsumer
import kafka
from datetime import datetime
from pymongo import MongoClient
import googleapiclient.discovery
import googleapiclient.errors
player_list = ["100T Asuna"]
player_list_channel = ['UCriJy6tyPtI5wrfZqXgRDag']
random_number = 200

def get_producer_obj():
    
    while(True):
        try:
            print('-------------------INSIDE-----------------')
            producer = KafkaProducer(bootstrap_servers='kafka2:8081',value_serializer=json_serializer)
            print(producer)
            return producer
        except kafka.errors.NoBrokersAvailable as e:
            print(e)
            print('---------------waiting for kaka-----------')
            time.sleep(1)
    


def json_serializer(data):
    return json.dumps(data).encode('utf-8')

def check_new_data(channel_id_final,channel_title,video_link,video_id_):
    index = 0
    index_2 = 0
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
        # mydb.insert_one(data)
        index_2 = index_2 + 1
    return updates
    

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
        # channel_title.append(player)
        # channel_id.append('UCriJy6tyPtI5wrfZqXgRDag')
        # index_ = index_ + 1


    video_link = []
    video_id_ = []
    channel_id_final = []
    for i in range(len(channel_id)):
        print("lates video for channel : ",channel_title[i])
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


def scraper_main(producer_obj):
    flag =0
    while(flag == 0):
        
        message = {
            'message':'pub1'
        }
        
        print("client hi")

        channel_id_final,channel_title,video_link,video_id_ = scrape_players()
        updates = check_new_data(channel_id_final,channel_title,video_link,video_id_)
        print('-------------------------------- NEW Data Producer 1--------------',updates)
        for update in updates:
            producer_obj.send('UCriJy6tyPtI5wrfZqXgRDag',update)
        time.sleep(21600)


    
        


if __name__=="__main__":
    producer_obj = get_producer_obj()
    scraper_main(producer_obj)