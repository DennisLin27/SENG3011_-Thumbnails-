from distutils.log import info
from gc import collect
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
import re
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

#some default options
collected_data["age_group"] = ""
collected_data["country"] = "Indonesia"
collected_data["city"] = ""
collected_data["symptoms"] = ["Abdominal pain", "Fever","Pain in the limbs"]
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
    collected_data["symptoms"] = json.loads(symptoms_returned)
    print(symptoms_returned)
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
      global collected_data
      collected_data["additional_info"] = additional_info
      return render_template('quiz_q6.html')
  else:
    return render_template('quiz_q6.html')

@app.route('/diseaseReport')
def disease_report():

    global collected_data
    db_data = collected_data.copy()
    db_data["symptoms"] = ",".join(db_data["symptoms"])
    conn = engine.connect()
    conn.execute(Info.insert(), [db_data])

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
    symptoms_list = collected_data["symptoms"]
    symptoms_converted = disease_symptoms.get_ids(symptoms_list)

    parameters2 = {
        "token": data['Token'],
        "symptoms": json.dumps(symptoms_converted), 
        "gender": 'male', 
        "year_of_birth": 1988,
        "language" : 'en-gb',
        "format": 'json'
    }
    response = requests.get("https://sandbox-healthservice.priaid.ch/diagnosis", params=parameters2)
    response = response.json()
    results = []
    
    if not response:
      disease_data = {}
      disease_data["Name"] = "No match"
      results.append(disease_data)
    else:
    
      for r in response:
          disease_data = {}

          #get the disease match
          disease_data["Name"] = r["Issue"]["Name"]
          disease_data["Accuracy"] = str(int(r["Issue"]["Accuracy"])) + "% match to your symptoms!"
          parameters = {
          "token": data['Token'],
          "language" : 'en-gb',
          "format": 'json'
          }

          #get a description of the disease
          description = requests.get("https://sandbox-healthservice.priaid.ch/issues/{}/info".format(str(r["Issue"]["ID"])), params=parameters)
          description = description.json()
          disease_data["Description"] = description["Description"]
          disease_data["MedicalCondition"] = description["MedicalCondition"]
          disease_data["Treatment"] = description["TreatmentDescription"]

          #call api to find outbreak information
          disease_data["Headline"] = "empty"
          disease_data["outbreakDescription"] = "empty"
          disease_data["url"] = "empty"

          disease = r["Issue"]["Name"]
          country = collected_data["country"]
          outbreak = requests.get("https://seng3011-dwen.herokuapp.com/articles?limit=20&start_date=2000-01-10&end_date=2022-01-20&key_terms={}&key_terms={}".format(disease, country))
          outbreak = outbreak.json()
          for o in outbreak:
              if (disease_data["Headline"] != "empty"):
                  break
              for l in o["locations"]:
                  if l == country:
                      disease_data["Headline"] = o["headline"].replace('\n', "")
                      disease_data["OutbreaksDescription"] = re.sub('\n.+\n\n', "", o["main_text"])
                      disease_data["OutbreaksDescription"] = disease_data["OutbreaksDescription"].replace('\n', "")
                      disease_data["url"] = o["url"]
                      break
          results.append(disease_data)
    print(results)
    return render_template('disease_report.html', results=results)

if __name__ == '__main__':
  app.run(debug=True, host='localhost')
