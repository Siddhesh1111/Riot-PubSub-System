from pymongo import MongoClient


def establish_conn():
    try:
            
            #conn = MongoClient("mongodb://user:password@mongodb2:27017")
            conn = MongoClient("mongodb://localhost:27017")
            
            
    except:  
            print("Could not connect to MongoDB")




