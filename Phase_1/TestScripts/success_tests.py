import requests
import re
import json
import filecmp

def result_append(description, expected_status_code, returned_status_code, status ):
    if (expected_status_code != returned_status_code):
        status = "TEST FAILED"
    result = {"input" : input, "expected_status_code":expected_status_code, "returned_status_code":returned_status_code, "status": status}
    with open('success_test_data.json', 'a') as outfile:
        json.dump(result, outfile, indent=2)

def geturl(route):
    base = "https://flask-service.boulmkfsb234o.us-east-1.cs.amazonlightsail.com/find"
    return base+route

def test_all_ebola():
    status = "TEST FAILED"
    input = "start_date=2010-03-04T00:00:00&end_date=2022-03-05T00:00:00&keyterms=ebola"
    p = requests.get(geturl(input))
    n = open("ebola_expected.json", "r")
    file = json.load(n)
    
    if (p.json() == n):
        status = "TEST PASSED"
    print(status)
    
    #result_append("Testing all ebola", "200", str(p.status_code), status)
    

if __name__ == "__main__":
    test_all_ebola()
