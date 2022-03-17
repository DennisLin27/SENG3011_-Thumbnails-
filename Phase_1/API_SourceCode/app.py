import re
from pymongo import MongoClient
from listeria import listeria_scraper
from ebola import ebola_scraper

cluster = "mongodb+srv://thumbnails:thumbnails@cluster0.lfkm3.mongodb.net/SENG3011?retryWrites=true&w=majority"
client = MongoClient(cluster)

# Select the database and the cluster 
db = client.SENG3011
collection = db.SENG3011_collection

def clear_db():
    result = collection.delete_many({})

def update_dp():
    results = []
    for x in listeria_scraper():
        result = collection.insert_one(x) 
    for x in ebola_scraper():
        result = collection.insert_one(x)

if __name__ == "__main__":
    clear_db()
    update_dp()

