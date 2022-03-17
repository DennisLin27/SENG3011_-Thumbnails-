import requests
import re
import json


def result_append(input, expected_code, returned_code, expected_message, returned_message):
    status = "TEST PASSED"
    if (expected_code != returned_code) or (expected_message != returned_message):
        status = "TEST FAILED"
    result = {"input" : input, "expected_error_code":expected_code, "returned_error_code":returned_code, "expected_error_message":expected_message, "returned_error_message":returned_message, "test_status":status}
    with open('errors_test_data.json', 'a') as outfile:
        json.dump(result, outfile, indent=2)


def test_invalid_dateformat():

    #base of api url
    base = "https://flask-service.boulmkfsb234o.us-east-1.cs.amazonlightsail.com/find"

    #Scenario
    #p = requests.get(base+"")
    #print(p.status_code)
    result_append("test", "test", "test", "test", "test")
    result_append("test", "test", "test", "test", "test")
    

if __name__ == "__main__":
    test_invalid_dateformat()
