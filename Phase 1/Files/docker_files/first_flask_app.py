# -*- coding: utf-8 -*-
"""
Created on Sat Sep 25 21:38:15 2021

@author: firstdb Kalyani
"""

import sys
from flask import Flask, request,redirect,url_for,render_template
from pymongo import MongoClient
from template import *





app = Flask(__name__,template_folder='template')


try:
           
        conn = MongoClient("mongodb://user:password@mongodb:27017")
        print(conn)
        
except:  
        print("Could not connect to MongoDB")
    
db = conn.firstdb
collection = db.user


@app.route("/",methods=["POST","GET"])
def home():
    if request.method == "POST":
        user = request.form['nm']
        ub_no = (request.form['no'])
        # print(user)
        
        # try:
           
        #     conn = MongoClient("mongodb://user:password@localhost:27117")
        #     print(conn)
        
        # except:  
        #     print("Could not connect to MongoDB")
            
        db = conn.firstdb
        collection = db.user
        data = {"userName":user,
                "UbNumber":ub_no
            }
        rec_id1 = collection.insert_one(data)
        x = collection.find()
 
        for values in x:
            print(values)
        
        # print("Data inserted with record ids",rec_id1)
        return "Operation Successful"
    else:
        return render_template("login.html")
    
@app.route("/data")
def login():
    
    # db = conn.firstdb
    # collection = db.user
    data2 = collection.find()
    

    return render_template("data.html",data_=data2)
   
@app.route("/<usr>")    
def user(usr):
    return f"<h1>{usr}</h1>"



if __name__ == "__main__":
    app.run(host = '0.0.0.0' , debug=True,use_reloader=False)