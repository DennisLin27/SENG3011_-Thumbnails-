from pymongo import MongoClient

cluster = "mongodb+srv://thumbnails:thumbnails@cluster0.lfkm3.mongodb.net/SENG3011?retryWrites=true&w=majority"
client = MongoClient(cluster)

# Select the database and the cluster 
db = client.SENG3011
collection = db.SENG3011_collection

def clear_db():
    result = collection.delete_many({})

#def update_dp():
