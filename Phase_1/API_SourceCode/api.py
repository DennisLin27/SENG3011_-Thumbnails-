from sqlite3 import DateFromTicks
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from flask_restx import Api, Resource, reqparse
import datetime
import re
  
cluster = "mongodb+srv://thumbnails:thumbnails@cluster0.lfkm3.mongodb.net/SENG3011?retryWrites=true&w=majority"
app = Flask(__name__)
client = MongoClient(cluster)

api = Api(app)

db = client.SENG3011

collection = db.SENG3011_collection

#RETRUNS ALL REPORTS IN DATABASE 
@api.route('/find', methods=['GET'])
class MainClass(Resource):
    def get(value):
        query = collection.find({})
        output = {}
        i = 0 
        for x in query:
            output[i] = x
            output[i].pop('_id')
            i+=1
        return jsonify(output)

#THIS ONE FINDS ANY MATCHES IN SPECIFIED FIELD 
@api.route('/find/<argument>/<value>/', methods=['GET'])
class MainClass(Resource):
    def get(argument, value):
        queryObject = {argument: value}
        query = collection.find(queryObject)
        output = {}
        i = 0
        for x in query:
            output[i] = x
            output[i].pop('_id')
            i+=1
        return jsonify(output)

#RETURNS REPORTS MATCHING DISEASE GIVEN 
@api.route('/find/disease/<value>', methods=['GET'])
class MainClass(Resource):
    def get(argument, value):
        query = collection.find( {"reports.diseases.0": value } )
        output = {}
        i = 0
        for x in query:
            output[i] = x
            output[i].pop('_id')
            i+=1
        return jsonify(output)

#RETURNS REPORTS MATCHING KEY TERMS
@api.route('/find/keyterms/<value>/', methods=['GET'])
class MainClass(Resource):
    def get(argument, value):
        query = collection.find( {"reports.diseases.0": value } ) # HOW DO I GET KEY TERMS 
        output = {}
        i = 0
        for x in query:
            output[i] = x
            output[i].pop('_id')
            i+=1
        return jsonify(output)

#RETURNS REPORTS MATCHING LOCATION
@api.route('/find/location/<value>/', methods=['GET'])
class MainClass(Resource):
    def get(argument, value):
        query = collection.find( {"reports.locations.0": value } )
        output = {}
        i = 0
        for x in query:
            output[i] = x
            output[i].pop('_id')
            i+=1
        return jsonify(output)

#RETURNS REPORTS MATCHING START AND END DATE
@api.route('/find/date/<value>/', methods=['GET'])
class MainClass(Resource):
    def get(argument, value):
        print(value)
        
        dates = value.split("&")
        print(dates)
        # Checks if dates are seperated by an &
        if (len(dates) != 2):
            print("Error: Dates must be seperated by a \"&\"")
            return -1 #REPLACE WITH ERROR CODE
        
        # Checks if dates are of format: YYYY-MM-DDTHH:mm:ss
        for date in dates:
            if not dateFormatCheck(date):
                print("Error: Dates must be of format: YYYY-MM-DDTHH:mm:ss") 
                return -1 #REPLACE WITH ERROR CODE
            
            if not dateFutureCheck(date):
                print("Error: Dates must not be in the future") 
                return -1 #REPLACE WITH ERROR CODE
              
        d1 = dateFormatCheck(dates[0])
        d2 = dateFormatCheck(dates[1])

        if not dateOrderCheck(d1,d2):
            print("Error: The first date must not be after the second date")
            return -1 #REPLACE WITH ERROR CODE


        query = collection.find({})
        output = {}
        i = 0
        for x in query:
            date = x.pop('date_of_publication')
            if checkDateRange(date, d1,d2):
                output[i] = x
                output[i].pop('_id')
                i+=1
            #print (date)
        return jsonify(output)

def dateFormatCheck(date):
    try:
        dateObject = datetime.datetime.strptime(date,'%Y-%m-%dT%H:%M:%S')
    except:
        return False
    return dateObject
        
def dateOrderCheck(d1,d2):
    print(d1,d2,d1<d2)
    if (d1 >= d2):
        return False
    return True

def dateFutureCheck(date):
    d1 = dateFormatCheck(date)
    if d1 > datetime.datetime.now():
        return False
    return True

def checkDateRange(date,d1,d2):
    temp_date = re.sub(r"[: ]","-",date)
    temp_date = re.sub(r"x","",temp_date)
    temp_date = re.sub(r"(--)","",temp_date)
    temp_date = re.sub(r"-$","",temp_date)
    elements = temp_date.split("-")
    if (len(elements) == 3):
        d3 = datetime.datetime.strptime(temp_date,'%Y-%m-%d')
    elif (len(elements) == 5):
        d3 = datetime.datetime.strptime(temp_date,'%Y-%m-%d-%H-%M')
    else:
        return False
    
    if not ((d1 <= d3) and (d3 <= d2)):
       return False
    
    return True








@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0')
