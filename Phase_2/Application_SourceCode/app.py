import requests
from flask import Flask, render_template, request, jsonify
import json
import disease_symptoms
import urllib

app = Flask(__name__)

#list of all countries
def all_countries():
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

selected_country = ""
collected_data = {}


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
    if request.method == "POST":
        countries = all_countries()
        global selected_country
        selected_country = request.form['country']
        global collected_data
        collected_data["country"] = selected_country
        #don't remove print statement
        print(selected_country)
        return render_template('quiz_q2.html', countries=countries)
    else:
        countries = all_countries()
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
      additional_info = urllib.parse.unquote(additional_info)
      print(additional_info)
      global collected_data
      collected_data["additional_info"] = additional_info
      return render_template('quiz_q6.html')
  else:
    return render_template('quiz_q6.html')

@app.route('/diseaseReport')
def disease_report():
  return render_template('disease_report.html')

if __name__ == '__main__':
  app.run(debug=True, host='localhost')
