from sqlite3 import DateFromTicks
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from pymongo import MongoClient
from flask_restx import Api, Resource, reqparse,fields
import time
import datetime
import re
  
cluster = "mongodb+srv://thumbnails:thumbnails@cluster0.lfkm3.mongodb.net/SENG3011?retryWrites=true&w=majority"
app = Flask(__name__)
client = MongoClient(cluster)

apii = Api(app,title = 'Outbreak Search API')
api = apii.namespace('', description = "Outbreak Search related endpoints")

db = client.SENG3011

collection = db.SENG3011_collection

response_model = api.model('response model', {
    'date_of_publication': fields.String(
        description = 'Date of report publication'
    ),
    'headline': fields.String(
        description = 'Headline of article'
    ),
    'main_text': fields.String(
        description = 'Main text of article'
    ),
    'reports': fields.Nested(
        api.model('reports',{
            'diseases': fields.String(
                description = 'Disease in mentioned in report'
            ),
            'event-date': fields.DateTime(
                description = 'date and time event'
            ),
            'locations': fields.String(
                description = 'List of locations menitoned in report'
            ),
            'syndromes': fields.String(
                description = 'List of syndromes mentioned in report '
            )
        })
    ),
    'url': fields.String(
        description = 'URL of article'
    )
})

# timestamp when end user access endpoints
timeStamp = time.time()
date = datetime.datetime.fromtimestamp(timeStamp).strftime("%Y-%m-%d %H:%M:%S")

logSnippet = {
    'team_name': 'Thumbnails',
    'access_time': date,
    'data_source': 'CDC Current Outbreak List'
}

#RETRUNS ALL REPORTS IN DATABASE 
@api.route('/findAll', methods=['GET'])
class MainClass(Resource):
    @api.doc(model=[response_model])
    def get(value):
        '''Search for all inputs in database'''
        query = collection.find({})
        output = {}
        i = 0 
        for x in query:
            output[i] = x
            output[i].pop('_id')
            i+=1
        timeStamp = time.time()
        logSnippet['access_time'] = date = datetime.datetime.fromtimestamp(timeStamp).strftime("%Y-%m-%d %H:%M:%S")
        response = {'data': output, 'log': logSnippet}
        return jsonify(response)

#THIS ONE FINDS ANY MATCHES IN SPECIFIED FIELD 
@api.route('/find<value>', methods=['GET'])
class MainClass(Resource):
    @api.doc(model=[response_model])
    @api.doc(responses={
        400 : 'Input date not seperated by a & character',
        401 : 'Dates in incorrect format (Expected : YYYY-MM-DDTHH:mm:ss)',
        402 : 'Invalid start and end dates (Cannot be future dates)',
        403 : 'Start Date is before End Date'
    })
    @api.doc(params = {'value' : 'Enter a start date, end date and optional keywords or locations in the form \n findstart_date=<date1>&end_date=<date2>&location<location>&keyterms=<term1,term2> '})
    
    def get(argument, value):
        '''Find reports based on start date, end date AND keywords OR location'''
        print(value)
        params = value.split("&")
        print(params)
        param_dict = {}
        for param in params:
            values = param.split("=")
            param_dict[values[0]] = values[1]

        start_date = param_dict['start_date']
        end_date = param_dict['end_date']
        location = ""
        keyterms = []
        if "location" in param_dict.keys(): 
            location =  param_dict['location']
        if "keyterms" in param_dict.keys():
            keyterms = param_dict['keyterms'].split(",")

        # Checks dates are in the correct format
        if not (dateFormatCheck(start_date) and dateFormatCheck(end_date)):
            return make_response(jsonify(error = "ERROR: Please enter dates in correct format: 'YYYY-MM-DDTHH:mm:ss'"),400)
        
        # Checks if dates are not in the future
        if not (dateFutureCheck(start_date) and dateFutureCheck(end_date)):
            return make_response(jsonify(error = "ERROR: Please enter in valid start and end dates. Dates cannot be future dates."),400)
        
        d1 = dateFormatCheck(start_date)
        d2 = dateFormatCheck(end_date)
        # Checks if dates are in the correct order
        if not dateOrderCheck(d1,d2):
            return make_response(jsonify(error = "ERROR: Please enter valid start and end dates. Start date must not be after end date"),400)

        output = get_dates(d1,d2)
        if location: 
            output = get_location(location, output)
        
        if keyterms:
            for term in keyterms:
                output = get_keyterms(term, output)

            
        timeStamp = time.time()
        logSnippet['access_time'] = date = datetime.datetime.fromtimestamp(timeStamp).strftime("%Y-%m-%d %H:%M:%S")
        response = {'data': output, 'log': logSnippet}
        return jsonify(response)

#RETURNS REPORTS MATCHING KEY TERMS
@api.route('/find/keyterms<value>', methods=['GET'])
class MainClass(Resource):
    @api.doc(model=[response_model])
    @api.doc(params = {'value' : 'Enter a keyterm'})
    def get(argument, value):
        '''Find Reports based on key terms'''
        query = collection.find({}) # HOW DO I GET KEY TERMS 
        
        keyterms = value.split(",")
        for term in keyterms:
            query = get_keyterms(term, query) 

        timeStamp = time.time()
        logSnippet['access_time'] = date = datetime.datetime.fromtimestamp(timeStamp).strftime("%Y-%m-%d %H:%M:%S")
        response = {'data': query, 'log': logSnippet}
        return jsonify(response)

#RETURNS REPORTS MATCHING LOCATION
@api.route('/find/location<value>', methods=['GET'])
class MainClass(Resource):
    @api.doc(model=[response_model])
    @api.doc(params = {'value' : 'Enter a location'})
    def get(argument, value):
        '''Find reports based on location'''
        print(value)
        query = collection.find({})
        output = get_location(value.lower(), query)
        
        timeStamp = time.time()
        logSnippet['access_time'] = date = datetime.datetime.fromtimestamp(timeStamp).strftime("%Y-%m-%d %H:%M:%S")
        response = {'data': output, 'log': logSnippet}
        return jsonify(response)

#RETURNS REPORTS MATCHING START AND END DATE
@api.route('/find/date<value>', methods=['GET'])
class MainClass(Resource):
    @api.doc(model=[response_model])
    @api.doc(params = {'value' : 'Enter a start and end date'})
    @api.doc(responses={
        400 : 'Input date not seperated by a & character',
        401 : 'Dates in incorrect format (Expected : YYYY-MM-DDTHH:mm:ss)',
        402 : 'Invalid start and end dates (Cannot be future dates)',
        403 : 'Start Date is before End Date'
    })
    def get(argument, value):        
        '''Find reports based on date''' 
        dates = value.split("&")

        # Checks if dates are seperated by an &
        if (len(dates) != 2):
            return make_response(jsonify(error = "ERROR: Please enter dates seperated by a '&'"),400)
        
        # Checks if dates are of format: YYYY-MM-DDTHH:mm:ss
        for date in dates:
            if not dateFormatCheck(date):
                return make_response(jsonify(error = "ERROR: Please enter dates in correct format: 'YYYY-MM-DDTHH:mm:ss'"),400)
            # Checks if dates are not in the future
            if not dateFutureCheck(date):
                return make_response(jsonify(error = "ERROR: Please enter in valid start and end dates. Dates cannot be future dates."),400)
              
        d1 = dateFormatCheck(dates[0])
        d2 = dateFormatCheck(dates[1])
        # Checks if dates are in the correct order
        if not dateOrderCheck(d1,d2):
            return make_response(jsonify(error = "ERROR: Please enter valid start and end dates. Start date must not be after end date"),400)


        query = collection.find({})
        output = []
        for x in query:
            date = x['date_of_publication']
            if checkDateRange(date, d1,d2):
                x.pop('_id')
                output.append(x)
        
        timeStamp = time.time()
        logSnippet['access_time'] = date = datetime.datetime.fromtimestamp(timeStamp).strftime("%Y-%m-%d %H:%M:%S")
        response = {'data': output, 'log': logSnippet}
        return jsonify(response)

def get_dates(d1,d2):
    query = collection.find({})
    output = []
    for x in query:
        date = x['date_of_publication']
        if checkDateRange(date, d1,d2):
            x.pop('_id')
            output.append(x)
    return output
        

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

def get_location(location, output):
    result = []
    for x in output:
        if "_id" in x.keys():
            x.pop('_id')
        lowercase_loc = []
        locations = x['reports']['locations']
        for loc in locations:
            lowercase_loc.append(loc.lower())
        if location.lower() in lowercase_loc:
            result.append(x)
    return result

def get_keyterms(term, output):
    result = []
    for x in output:
        if "_id" in x.keys():
            x.pop('_id')
        lowercase_dis = []
        diseases = x['reports']['diseases']
        lowercase_main = x['main_text'].lower()
        lowercase_headline = x['headline'].lower()
        for dis in diseases:
            lowercase_dis.append(dis.lower())
        if (term.lower() in lowercase_dis) or ((term.lower() in lowercase_main) or (term.lower() in lowercase_headline)):
            result.append(x)
    return result
        


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

        
if __name__ == '__main__':
    app.run(host='0.0.0.0')
