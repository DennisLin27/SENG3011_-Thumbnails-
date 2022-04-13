from distutils.log import info
from tkinter import Variable
import requests
from flask import Flask, render_template, request, jsonify
import disease_symptoms
import urllib
import hmac, hashlib
import enum 
import base64
import json
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select, func

app = Flask(__name__)

#list of all countries
def get_all_countries():
  page = requests.get("https://countriesnow.space/api/v0.1/countries")
  data = page.json()["data"]
  countries = []
  for d in data:
    countries.append(d["country"])
  return countries

#list of all cities given the state
def get_cities(country_given):
  page = requests.get("https://countriesnow.space/api/v0.1/countries")
  data = page.json()["data"]
  for d in data:
    country = d['country']
    cities = d["cities"]
    if (country == country_given):
      return cities

all_countries = get_all_countries()
selected_country = ""
collected_data = {}
collected_data["age_group"] = ""
collected_data["country"] = ""
collected_data["city"] = ""
collected_data["symptoms"] = []
collected_data["symptoms_length"] = ""
collected_data["additional_info"] = ""

#create database
meta = MetaData()
engine = create_engine('sqlite:///FormInfo.db', echo = True)
Info = Table(
    'actors', meta,
    Column('id', Integer, primary_key = True, autoincrement=True),
    Column('age_group', String),
    Column('country', String),
    Column('city', String),
    Column('symptoms', String),
    Column('symptoms_length', String),
    Column('additional_info', String),
)
meta.create_all(engine)

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/chemist')
def chemist():
  return render_template('chemist.html')

@app.route('/doctor')
def doctor():
  return render_template('doctor.html')

@app.route('/age', methods=['POST', 'GET'])
def age():
  if request.method == "POST":
    age = request.form['age']
    global collected_data
    collected_data["age_group"] = age
    print(age)
  return render_template('quiz_q1.html')

@app.route('/location', methods=['POST', 'GET'])
def select_country():
    global all_countries
    if request.method == "POST":
        countries = all_countries
        global selected_country
        selected_country = request.form['country']
        global collected_data
        collected_data["country"] = selected_country
        #don't remove print statement
        print(selected_country)
        return render_template('quiz_q2.html', countries=countries)
    else:
        countries = all_countries
        return render_template('quiz_q2.html', countries=countries)

@app.route('/location/city', methods=['POST', 'GET'])
def select_city():
    global selected_country
    if request.method == "POST":
        cities = get_cities(selected_country)
        #don't remove print statement
        print("random city" + cities[0])
        city = request.form['city']
        global collected_data
        collected_data["city"] = city
        return render_template('quiz_q3.html', cities=cities)
    else:
        cities = get_cities(selected_country)
        #don't remove print statement
        print("random city:  " + cities[0])
        return render_template('quiz_q3.html', cities=cities)

@app.route('/symptoms', methods=['POST', 'GET'])
def symptoms():
  if request.method == "POST":
    symptoms = disease_symptoms.get_symptoms()
    symptoms_returned = request.form['symptoms']
    global collected_data
    collected_data["symptoms"] = list(json.loads(symptoms_returned))
    return render_template('quiz_q4.html', symptoms=symptoms)
  else:
    symptoms = disease_symptoms.get_symptoms()
  return render_template('quiz_q4.html', symptoms=symptoms)

@app.route('/symptoms/length', methods=['POST', 'GET'])
def symptoms_length():
  if request.method == "POST":
      length = request.form['length']
      global collected_data
      collected_data["symptom_length"] = length
      print(length)
  return render_template('quiz_q5.html')

@app.route('/additionalInfo', methods=['POST', 'GET'])
def additional_info():
  if request.method == "POST":
      additional_info = request.form['data']
      additional_info = (urllib.parse.unquote(additional_info)).strip()
      print(additional_info)
      global collected_data
      collected_data["additional_info"] = additional_info
      db_data = collected_data
      db_data["symptoms"] = ",".join(db_data["symptoms"])
      conn = engine.connect()
      conn.execute(Info.insert(), [db_data])
      return render_template('quiz_q6.html')
  else:
    return render_template('quiz_q6.html')

@app.route('/diseaseReport')
def disease_report():
    username = 'z5234001@ad.unsw.edu.au'
    url = 'https://sandbox-authservice.priaid.ch/login'
    password = 'r6KSm24LbMa78Tfd5'
    rawHashString = hmac.new(bytes(password, encoding='utf-8'),(url.encode('utf-8')), digestmod=hashlib.md5).digest()
    computedHashString = base64.b64encode(rawHashString).decode()
    bearer_creds = username + ':' + computedHashString
    postHeaders = {
        'Authorization': 'Bearer {}'.format(bearer_creds)
    }
    responsePost = requests.post(url,headers=postHeaders)
    data = json.loads(responsePost.text)

    parameters2 = {
        "token": data['Token'],
        "symptoms": json.dumps([10,11,12]), 
        "gender": 'male', 
        "year_of_birth": 1988,
        "language" : 'en-gb',
        "format": 'json'
    }
    response = requests.get("https://sandbox-healthservice.priaid.ch/diagnosis", params=parameters2)
    response = response.json()
    results = []
    api_response = requests.get('http://13.52.98.118/articles?key_term=flu&location=Australia&start_date=1900-03-03%2000%3A00%3A00&end_date=2022-03-03%2000%3A00%3A00&limit=1')
    api_response = api_response.json()

    for r in response:
      print(r)
      new_dict = {}
      new_dict["Name"] = r["Issue"]["Name"]
      new_dict["Accuracy"] = str(int(r["Issue"]["Accuracy"])) + "% match to your symptoms!"
      try:
        key_term = r["Issue"]["Name"]
        if (key_term == "Listeria infection"):
          key_term = "listeriosis"
        api_response = requests.get('http://13.52.98.118/articles?key_term='+str(key_term)+'&location=Australia&start_date=1900-03-03%2000%3A00%3A00&end_date=2022-03-03%2000%3A00%3A00&limit=1')
        api_response = api_response.json()[0]
        new_dict["Country"] = "Outbreaks near " + api_response["country"]
        new_dict["Description"] = api_response["description"]
        new_dict["Links"] = api_response["links"][0] 
      except:
        new_dict["Country"] = "Disease found in country:"
        new_dict["Description"] = "Article description:"
        new_dict["Links"] = "links:"
      results.append(new_dict)
    #print(results)
    
    return render_template('disease_report.html', results=results)

if __name__ == '__main__':
  app.run(debug=True, host='localhost')
