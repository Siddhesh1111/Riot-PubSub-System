import googleapiclient.discovery
import googleapiclient.errors




def scrape_players():

    player_list = ["SEN Tenz","TSM FTX WARDELL","100T Asuna","100T Hiko","SEN Sinatraa","SEN Sick","ShahZaM","ScreaM","AverageJonas","pkSidlol_"]

    api_key = 'AIzaSyCKkollyvp90wh9HRrEdiGI5ohs2G15EgU'
    youtube = googleapiclient.discovery.build('youtube', 'v3',developerKey=api_key)
    video_link = []
    video_id_ = []
    channel_id = []
    channel_title = []
    for player in player_list:
        request = youtube.search().list(
                part="snippet",
                q = player,
                type ="channel"
            )
        response = request.execute()
        channel_id.append(response['items'][0]['snippet']['channelId'])
        channel_title.append(response['items'][0]['snippet']['channelTitle'])


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

    return channel_id_final,channel_title,video_link,video_id_