

from flask_socketio import SocketIO, emit,send
from flask import Flask, render_template, url_for, copy_current_request_context,session,request
from random import random
from time import sleep
from threading import Thread, Event
import json




app = Flask(__name__,template_folder='template')
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)
session_id = {}





class pub_sub_temp:
    def __init__(self):
        self.sub_list = {}

        self.sub_list['greater'] = []
        self.sub_list['less'] = []
        self.data_greater = []
        self.data_less = []

    def sub(self,data):
        
        # for topic in data.keys():
        #     if(topic not in topics.keys()):
        #         self.topics[topic] = []
        #         self.topics[topic].append(data['userName'])
        #     else:
        #         self.topics[topic].append(data['userName'])

        if data['value']=='greater':
            print('-----------------------Subscription added for user : ',data['user_name'])
            self.sub_list['greater'].append(data['user_name'])
        else:
            print('-----------------------Subscription added for user : ',data['user_name'])
            self.sub_list['less'].append(data['user_name'])


    def notify(self,number,user,session_id):
        
        if number>5:
            users =  self.sub_list['greater']
            for userName in users:
                # temp_list =dict()
                if userName == user:
                    # temp_list={
                    #         'player_name' : 'p1',
                    #         'link':[1,2,3,4]
                    #     }
                    temp_list = [1,2,3,4]

                    
                        
                    
                    obj = json.dumps(temp_list)
                    print(type(obj))
                    socketio.emit('newnumber', {'data':temp_list} ,room=session_id,namespace='/test',json=True)
        # else:
        #     users =  self.sub_list['less']
        #     for userName in users:
        #         temp_list =dict()
        #         if userName == user:
        #             temp_list = [
        #                 {
        #                     '1' : 'yes',
        #                     '2' : 'No'
        #                 },
        #                 {
        #                     '1' : 'yes',
        #                     '2' : 'No'
        #                 }
        #             ]
        #             obj = json.dump(temp_list)
        #             socketio.emit('newnumber', {'data':obj},room=session_id,namespace='/test')
                    
        

    def notify_new(self,number):
        if number > 5:
            users =  self.sub_list['greater']
            # temp_list = [1,2,3,4]

                    
                        
                    
            # obj = json.dumps(temp_list)
            # print(type(obj))
            # socketio.emit('newnumber', {'data':temp_list} ,room=session_id,namespace='/test',json=True)
            for userName in users:
                session_id_value = session_id[userName]
                temp_list = [
                    {
                        'player' : 'player1',
                        'video' : ['1','2']
                    },
                    {
                        'player':'player2',
                        'video' : ['1','2']
                    }
                ]
                obj = json.dumps(temp_list)
                socketio.emit('newnumber', {'data':obj},room = session_id_value,namespace='/test')
        else:
            users =  self.sub_list['less']
            for userName in users:
                session_id_value = session_id[userName]
                socketio.emit('newnumber', {'number': number,'user':userName},room = session_id_value,namespace='/test')

    def publisher(self,number):
        if number>5:
            if number not in self.data_greater:
                self.data_greater.append(number)
                print('--------------------------------------------------------------------------------------------------')
                # socketio.emit('newdata', {'number': number}, namespace='/test')
                self.notify_new(number)
        else:
            if number not in self.data_less:
                self.data_less.append(number)
                print('--------------------------------------------------------------------------------------------------')
                # socketio.emit('newdata', {'number': number}, namespace='/test')
                self.notify_new(number)




#turn the flask app into a socketio app


#random number Generator Thread
thread = Thread()
thread_stop_event = Event()
pub_sub_obj = pub_sub_temp()







# def soc():
#     global socketio
    
#     return socketio

def randomNumberGenerator():
    """
    Generate a random number every 1 second and emit to a socketio instance (broadcast)
    Ideally to be run in a separate thread?
    """
    #infinite loop of magical random numbers
    
    print("Making random numbers")
    while not thread_stop_event.isSet():
        number = round(random()*10, 3)
        print("------------------------NEW Number-------------------",number)
        # user_name = "prashant"
        
       
        # user_name = session["user"]
        
        
        pub_sub_obj.publisher(number)
        socketio.sleep(1)
        print('------------------------------------------------------------------------')
        # socketio.emit('newnumber', {'number': number}, namespace='/test')
        
        


@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    

    return render_template('index_practice.html')

@app.route("/login",methods=["POST","GET"])
def login():
    
    if request.method == "POST":
        user_name_ = request.form['nm']
        value_ =  request.form['no']
        session["user"] = user_name_
        data = {
            "user_name" : user_name_ ,
            "value" : value_
        }
        pub_sub_obj.sub(data)
        return render_template('index.html')

@socketio.on('notify', namespace='/test')
def notify_event(payload):

    global session_id
    user_name = session["user"]
    session_id_ = session_id[user_name]
    print(user_name)

    # socketio.emit('newnumber', {'number': payload['newnumber'],'user':user_name},namespace='/test',room = session_id_)

    
    # socketio.emit('newnumber', {'number': payload['newnumber'],'user':user},room = session_id)
        

    pub_sub_obj.notify(payload['newnumber'],user_name,session_id_)
    


@socketio.on('my event', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    global session_id
    print('Client connected')
    user = session["user"]
    print("-----------------------------------",user)
    session_id[user] = request.sid

    #Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(randomNumberGenerator)


    

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    
    socketio.run(app)