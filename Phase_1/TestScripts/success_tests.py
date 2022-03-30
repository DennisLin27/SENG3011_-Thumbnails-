import requests
import re
import json
import filecmp

def result_append(description, expected_status_code, returned_status_code, status ):
    if (expected_status_code != returned_status_code):
        status = "TEST FAILED"
    result = {"description" : description, "expected_status_code":expected_status_code, "returned_status_code":returned_status_code, "status": status}
    with open('success_test_data.json', 'a') as outfile:
        json.dump(result, outfile, indent=2)

def geturl(route):
    base = "https://flask-service.boulmkfsb234o.us-east-1.cs.amazonlightsail.com/find"
    return base+route

def test_all_ebola():
    status = "TEST FAILED"
    input = "start_date=2010-03-04T00:00:00&end_date=2022-03-05T00:00:00&keyterms=ebola"
    p = requests.get(geturl(input))

    with open('ebola_expected.json', 'r') as f:
        data = json.load(f)
    if ((p.json()) != data):
        status = "TEST PASSED"
    result_append("Testing all ebola", "200", str(p.status_code), status)

def test_all_listeria():
    status = "TEST FAILED"
    input = "start_date=2010-03-04T00:00:00&end_date=2022-03-05T00:00:00&keyterms=listeriosis"
    p = requests.get(geturl(input))
    
    with open('listeria_expected.json', 'r') as f:
        data = json.load(f)
    if ((p.json()) != data):
        status = "TEST PASSED"
    result_append("Testing all listeria", "200", str(p.status_code), status)

def test_all_outputs():
    status = "TEST FAILED"
    input = "All"
    p = requests.get(geturl(input))
    
    with open('findAll_expected.json', 'r') as f:
        data = json.load(f)
    if ((p.json()) != data):
        status = "TEST PASSED"
    result_append("Testing all results", "200", str(p.status_code), status)

def test_location_new_york():
    status = "TEST FAILED"
    input = "start_date=2010-03-04T00:00:00&end_date=2022-03-05T00:00:00&location=new york"
    p = requests.get(geturl(input))

    with open('new_york_expected.json', 'r') as f:
        data = json.load(f)
    if ((p.json()) != data):
        status = "TEST PASSED"
    result_append("Testing location: New York", "200", str(p.status_code), status)

def test_keyword_deli():
    status = "TEST FAILED"
    input = "start_date=2010-03-04T00:00:00&end_date=2022-1-05T00:00:00&location=new york&keyterms=deli"
    p = requests.get(geturl(input))

    with open('deli_expected.json', 'r') as f:
        data = json.load(f)
    if ((p.json()) != data):
        status = "TEST PASSED"
    result_append("Testing keyword: deli", "200", str(p.status_code), status)

def test_keyword_multiple():
    status = "TEST FAILED"
    input = "start_date=2010-03-04T00:00:00&end_date=2022-1-05T00:00:00&location=new york&keyterms=listeria,queso"
    p = requests.get(geturl(input))
    with open('multiple_keyterms_expected.json', 'r') as f:
        data = json.load(f)
    if ((p.json()) != data):
        status = "TEST PASSED"
    result_append("Testing keyword: Listeria, Queso", "200", str(p.status_code), status)


if __name__ == "__main__":
    test_all_ebola()
    test_all_listeria()
    test_all_outputs()
    test_location_new_york()
    test_keyword_deli()
    test_keyword_multiple()
